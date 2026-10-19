# sign_classifier.py
# Clasificador ML (Random Forest / MLP) sobre features geometricas + desempate por grupos.

from __future__ import annotations

import csv
import os
from typing import Dict, List, Optional, Tuple

import joblib
import numpy as np

from .feature_extractor import (
    FEATURE_NAMES,
    N_FEATURES,
    extract_features,
    features_to_dict,
)

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.neural_network import MLPClassifier
    from sklearn.preprocessing import LabelEncoder
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score
except ImportError as e:
    raise ImportError(
        "scikit-learn es necesario. Instale: pip install scikit-learn joblib"
    ) from e


# Puntos crudos de MediaPipe (21 x [x, y, z]) guardados junto a cada muestra.
# Van antes de las features para que su posicion en el CSV no cambie aunque se
# agreguen o corrijan features: al entrenar, las features se recalculan desde aqui.
LANDMARK_COLUMNS: List[str] = [f"lm{i}_{axis}" for i in range(21) for axis in ("x", "y", "z")]


class SignClassifier:
    """
    Recolecta muestras, entrena y predice letras A-Z con umbral de confianza.

    Uso tipico:
        clf = SignClassifier()
        clf.collect_sample("B", landmarks)
        clf.train()
        clf.save_model()
        letter, conf = clf.predict(landmarks)
    """

    LETTERS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    def __init__(
        self,
        samples_csv: Optional[str] = None,
        model_path: Optional[str] = None,
        classifier_type: str = "rf",
        confidence_threshold: float = 0.85,
        samples_per_letter: int = 60,
        n_estimators: int = 200,
        language: Optional[str] = None,
    ) -> None:
        self.language = language or "es"
        self.letters: List[str] = list(self.LETTERS)
        try:
            from src.config import (
                SIGN_ALPHABETS,
                SIGN_CLASSIFIER_TYPE,
                SIGN_MODEL_FILES,
                SIGN_CONFIDENCE_THRESHOLD,
                SIGN_MODEL_PATH,
                SIGN_SAMPLES_CSV,
                SIGN_SAMPLES_PER_LETTER,
                SIGN_USE_ML_TIEBREAKERS,
            )
            default_csv = SIGN_SAMPLES_CSV
            default_model = SIGN_MODEL_PATH
            default_type = SIGN_CLASSIFIER_TYPE
            default_conf = SIGN_CONFIDENCE_THRESHOLD
            default_per = SIGN_SAMPLES_PER_LETTER
            default_tiebreak = SIGN_USE_ML_TIEBREAKERS
            # Cada idioma tiene su propio alfabeto, dataset y modelo (pt = LIBRAS, en = ASL).
            if self.language in SIGN_MODEL_FILES:
                default_csv, default_model = SIGN_MODEL_FILES[self.language]
                self.letters = list(SIGN_ALPHABETS[self.language])
        except Exception:
            root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            data_dir = os.path.join(root, "data", "sign_language")
            default_csv = os.path.join(data_dir, "sign_samples.csv")
            default_model = os.path.join(data_dir, "sign_classifier.joblib")
            default_type = "rf"
            default_conf = 0.55
            default_per = 60
            default_tiebreak = False

        self.samples_csv = samples_csv or default_csv
        self.model_path = model_path or default_model
        self.classifier_type = (classifier_type or default_type).lower()
        self.confidence_threshold = confidence_threshold if confidence_threshold else default_conf
        self.samples_per_letter = samples_per_letter or default_per
        self.n_estimators = n_estimators
        # Los desempates describen formas del alfabeto original; no aplican a LIBRAS.
        self.use_tiebreakers = default_tiebreak and self.language != "pt"

        self._model = None
        self._label_encoder: Optional[LabelEncoder] = None
        self._last_letter: Optional[str] = None
        self._stability_count = 0
        # Rasgos geometricos ya calculados por el clasificador en el frame.
        # Repaso los reutiliza sin ejecutar otro extractor.
        self._last_features: Optional[np.ndarray] = None
        try:
            from src.config import SIGN_STABILITY_FRAMES
            self._stability_threshold = max(4, int(SIGN_STABILITY_FRAMES) - 2)
        except Exception:
            self._stability_threshold = 6

        if os.path.isfile(self.model_path):
            self.load_model()

    def _ensure_csv_header(self) -> bool:
        """Crea el CSV si no existe. Retorna True si el CSV guarda landmarks crudos."""
        os.makedirs(os.path.dirname(self.samples_csv) or ".", exist_ok=True)
        if os.path.isfile(self.samples_csv):
            with open(self.samples_csv, "r", encoding="utf-8", newline="") as f:
                header = next(csv.reader(f), [])
            return len(header) > 1 and header[1] == LANDMARK_COLUMNS[0]
        with open(self.samples_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["letter"] + LANDMARK_COLUMNS + FEATURE_NAMES)
        return True

    @staticmethod
    def _landmarks_row(hand_landmarks) -> List[float]:
        row: List[float] = []
        for lm in hand_landmarks[:21]:
            if isinstance(lm, dict):
                row += [float(lm["x"]), float(lm["y"]), float(lm.get("z", 0.0))]
            else:
                row += [float(lm[0]), float(lm[1]), float(lm[2]) if len(lm) > 2 else 0.0]
        return row

    def collect_sample(self, letter: str, hand_landmarks) -> bool:
        """Guarda una fila en el CSV. Retorna False si no hay landmarks validos."""
        letter = letter.upper().strip()
        if letter not in self.letters:
            return False
        feat = extract_features(hand_landmarks)
        if feat is None:
            return False
        with_landmarks = self._ensure_csv_header()
        if not with_landmarks and not getattr(self, "_warned_old_csv", False):
            self._warned_old_csv = True
            print(
                f"[Senas] {self.samples_csv} tiene el formato antiguo (sin landmarks). "
                "Renombrelo para empezar un CSV nuevo que guarde los puntos de la mano."
            )
        row = [letter]
        if with_landmarks:
            row += self._landmarks_row(hand_landmarks)
        row += feat.tolist()
        with open(self.samples_csv, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(row)
        return True

    def load_samples(self) -> Tuple[np.ndarray, np.ndarray]:
        if not os.path.isfile(self.samples_csv):
            raise FileNotFoundError(
                f"No hay datos en {self.samples_csv}. Ejecute collect_sign_samples.py primero."
            )
        rows_x: List[List[float]] = []
        rows_y: List[str] = []
        n_lm = len(LANDMARK_COLUMNS)
        with open(self.samples_csv, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, [])
            with_landmarks = len(header) > 1 and header[1] == LANDMARK_COLUMNS[0]
            for row in reader:
                if not row:
                    continue
                label = row[0].strip().upper()
                if label not in self.letters:
                    continue
                try:
                    if with_landmarks:
                        # Features recalculadas con el extractor actual.
                        coords = [float(v) for v in row[1 : 1 + n_lm]]
                        lms = [
                            {"x": coords[i], "y": coords[i + 1], "z": coords[i + 2]}
                            for i in range(0, n_lm, 3)
                        ]
                        feat = extract_features(lms)
                        if feat is None:
                            continue
                        vec = feat.tolist()
                    else:
                        # CSV antiguo: solo tiene las features ya calculadas.
                        vec = [float(row[header.index(name)]) for name in FEATURE_NAMES]
                except (IndexError, ValueError):
                    continue
                if len(vec) != N_FEATURES:
                    continue
                rows_x.append(vec)
                rows_y.append(label)
        if not rows_x:
            raise ValueError("El CSV no contiene muestras validas.")
        return np.array(rows_x, dtype=np.float32), np.array(rows_y)

    def _build_estimator(self):
        if self.classifier_type == "mlp":
            return MLPClassifier(
                hidden_layer_sizes=(64, 32),
                max_iter=400,
                random_state=42,
                early_stopping=True,
                validation_fraction=0.1,
            )
        return RandomForestClassifier(
            n_estimators=self.n_estimators,
            random_state=42,
            n_jobs=-1,
            class_weight="balanced_subsample",
        )

    def train(self, test_size: float = 0.15) -> Dict[str, float]:
        X, y = self.load_samples()
        self._label_encoder = LabelEncoder()
        y_enc = self._label_encoder.fit_transform(y)

        if len(X) < 30:
            self._model = self._build_estimator()
            self._model.fit(X, y_enc)
            return {"accuracy": 1.0, "n_samples": float(len(X)), "note": "pocos_datos"}

        X_train, X_test, y_train, y_test = train_test_split(
            X, y_enc, test_size=test_size, random_state=42, stratify=y_enc
        )
        self._model = self._build_estimator()
        self._model.fit(X_train, y_train)
        acc = float(accuracy_score(y_test, self._model.predict(X_test)))
        return {"accuracy": acc, "n_samples": float(len(X)), "n_train": float(len(X_train))}

    def save_model(self, path: Optional[str] = None) -> str:
        if self._model is None or self._label_encoder is None:
            raise RuntimeError("Entrene el modelo antes de guardar (train()).")
        path = path or self.model_path
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        joblib.dump(
            {
                "model": self._model,
                "label_encoder": self._label_encoder,
                "classifier_type": self.classifier_type,
                "feature_names": FEATURE_NAMES,
            },
            path,
        )
        self.model_path = path
        return path

    def load_model(self, path: Optional[str] = None) -> bool:
        path = path or self.model_path
        if not os.path.isfile(path):
            return False
        data = joblib.load(path)
        self._model = data["model"]
        self._label_encoder = data["label_encoder"]
        self.model_path = path
        return True

    def is_trained(self) -> bool:
        return self._model is not None and self._label_encoder is not None

    def known_letters(self) -> set:
        """Letras que el modelo cargado sabe reconocer (vacio si no hay modelo)."""
        if self._label_encoder is None:
            return set()
        return {str(c) for c in self._label_encoder.classes_}

    def _proba_dict(self, features: np.ndarray) -> Dict[str, float]:
        assert self._model is not None and self._label_encoder is not None
        proba = self._model.predict_proba(features.reshape(1, -1))[0]
        classes = self._label_encoder.classes_
        return {str(c): float(p) for c, p in zip(classes, proba)}

    def _apply_tiebreakers(
        self,
        letter: str,
        confidence: float,
        proba: Dict[str, float],
        features: np.ndarray,
        hand_landmarks,
    ) -> Tuple[str, float]:
        """Refina la letra en grupos de confusion frecuente."""
        f = features_to_dict(features)
        if not f:
            return letter, confidence

        thumb = f["finger_thumb"] > 0.5
        index = f["finger_index"] > 0.5
        middle = f["finger_middle"] > 0.5
        ring = f["finger_ring"] > 0.5
        pinky = f["finger_pinky"] > 0.5
        four_up = f["four_fingers_up"] > 0.5
        dist_ti = f["dist_thumb_index"]
        sep_im = f["index_middle_sep"]
        cover = f["thumb_cover_norm"]
        thumb_between = f["thumb_between"] > 0.6
        fist_compact = f["fist_compactness"]

        candidates = sorted(proba.items(), key=lambda x: x[1], reverse=True)[:3]
        top_letters = {c[0] for c in candidates}

        # B vs K
        if letter in ("B", "K") or top_letters & {"B", "K"}:
            if four_up and not thumb_between:
                letter, confidence = "B", max(confidence, proba.get("B", confidence))
            elif index and middle and not ring and not pinky and thumb_between:
                letter, confidence = "K", max(confidence, proba.get("K", confidence))

        # U vs V
        if letter in ("U", "V") or top_letters & {"U", "V"}:
            if index and middle and not ring and not pinky:
                if sep_im < 0.22:
                    letter, confidence = "U", max(confidence, proba.get("U", confidence))
                elif sep_im > 0.32:
                    letter, confidence = "V", max(confidence, proba.get("V", confidence))

        # D vs C vs G vs O
        if letter in ("D", "C", "G", "O", "F") or top_letters & {"D", "C", "G", "O", "F"}:
            ext_non_thumb = sum([index, middle, ring, pinky])
            if dist_ti < 0.28 and four_up:
                letter, confidence = "B", max(confidence, proba.get("B", 0.0))
            elif dist_ti < 0.32 and index and (middle or ring) and not four_up:
                letter, confidence = "F", max(confidence, proba.get("F", confidence))
            elif index and not middle and not ring and not pinky and dist_ti > 0.45:
                letter, confidence = "D", max(confidence, proba.get("D", confidence))
            elif dist_ti > 0.38 and ext_non_thumb >= 3 and not (index and middle and ring and pinky):
                letter, confidence = "C", max(confidence, proba.get("C", confidence))
            elif thumb and index and not middle and not ring and not pinky and dist_ti > 0.35:
                letter, confidence = "G", max(confidence, proba.get("G", confidence))
            elif dist_ti < 0.35 and fist_compact < 1.1 and ext_non_thumb >= 3:
                letter, confidence = "O", max(confidence, proba.get("O", confidence))

        # A vs S vs E vs T
        if letter in ("A", "S", "E", "T") or top_letters & {"A", "S", "E", "T"}:
            if not index and not middle and fist_compact < 1.05:
                if cover >= 0.65:
                    letter, confidence = "M", max(confidence, proba.get("M", 0.0))
                elif cover >= 0.45:
                    letter, confidence = "N", max(confidence, proba.get("N", 0.0))
                elif thumb_between:
                    letter, confidence = "T", max(confidence, proba.get("T", confidence))
                elif thumb and dist_ti > 0.4:
                    letter, confidence = "S", max(confidence, proba.get("S", confidence))
                elif not thumb or fist_compact < 0.95:
                    letter, confidence = "A", max(confidence, proba.get("A", confidence))
                else:
                    letter, confidence = "E", max(confidence, proba.get("E", confidence))

        # M vs N (si el modelo eligio M/N o estan en top3)
        if letter in ("M", "N") or top_letters & {"M", "N"}:
            if cover >= 0.7:
                letter, confidence = "M", max(confidence, proba.get("M", confidence))
            elif cover >= 0.45:
                letter, confidence = "N", max(confidence, proba.get("N", confidence))

        return letter, min(1.0, confidence)

    def predict(self, hand_landmarks) -> Tuple[Optional[str], float]:
        """
        Predice letra y confianza. Retorna (None, 0.0) si confianza < umbral o sin modelo.
        """
        if not self.is_trained():
            return None, 0.0
        feat = extract_features(hand_landmarks)
        if feat is None:
            return None, 0.0
        self._last_features = feat.copy()

        proba = self._proba_dict(feat)
        letter = max(proba, key=proba.get)
        confidence = proba[letter]

        if self.use_tiebreakers:
            letter, confidence = self._apply_tiebreakers(
                letter, confidence, proba, feat, hand_landmarks
            )

        if confidence < self.confidence_threshold:
            return None, confidence
        return letter, confidence

    def predict_raw(self, hand_landmarks) -> Tuple[Optional[str], float, Dict[str, float]]:
        """Prediccion sin umbral (util para depuracion)."""
        if not self.is_trained():
            return None, 0.0, {}
        feat = extract_features(hand_landmarks)
        if feat is None:
            return None, 0.0, {}
        self._last_features = feat.copy()
        proba = self._proba_dict(feat)
        letter = max(proba, key=proba.get)
        conf = proba[letter]
        if self.use_tiebreakers:
            letter, conf = self._apply_tiebreakers(letter, conf, proba, feat, hand_landmarks)
        return letter, conf, proba

    def letter_for_display(self, hand_landmarks) -> Tuple[Optional[str], float]:
        """
        Letra para mostrar en UI: estable si puede; si no, vista previa con umbral mas bajo.
        """
        if hand_landmarks is None:
            self._stability_count = 0
            self._last_letter = None
            self._last_features = None
            return None, 0.0

        self._last_features = None

        stable = self.classify_with_stability(hand_landmarks)
        if stable is not None:
            _, conf, _ = self.predict_raw(hand_landmarks)
            return stable, conf

        letter, conf, _ = self.predict_raw(hand_landmarks)
        try:
            from src.config import SIGN_DISPLAY_CONFIDENCE_THRESHOLD
            disp_thr = float(SIGN_DISPLAY_CONFIDENCE_THRESHOLD)
        except Exception:
            disp_thr = 0.45
        if letter and conf >= disp_thr:
            return letter, conf
        return None, conf

    def latest_features(self) -> Optional[np.ndarray]:
        """Copia de los rasgos ya usados para clasificar el frame actual."""
        return self._last_features.copy() if self._last_features is not None else None

    def classify_with_stability(self, hand_landmarks) -> Optional[str]:
        letter, _ = self.predict(hand_landmarks)
        if letter is None:
            self._stability_count = 0
            self._last_letter = None
            return None
        if letter == self._last_letter:
            self._stability_count += 1
            if self._stability_count >= self._stability_threshold:
                return letter
        else:
            self._last_letter = letter
            self._stability_count = 1
        return None

    def reset_stability(self) -> None:
        self._last_letter = None
        self._stability_count = 0

    def count_samples_for_letter(self, letter: str) -> int:
        return self.count_samples_per_letter().get(letter.upper().strip(), 0)

    def remove_samples_for_letter(self, letter: str) -> int:
        """Elimina del CSV todas las filas de una letra. Retorna cuantas borro."""
        letter = letter.upper().strip()
        if letter not in self.letters or not os.path.isfile(self.samples_csv):
            return 0
        kept: List[List[str]] = []
        removed = 0
        with open(self.samples_csv, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if header is None:
                return 0
            for row in reader:
                if not row:
                    continue
                if row[0].strip().upper() == letter:
                    removed += 1
                else:
                    kept.append(row)
        with open(self.samples_csv, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(header)
            w.writerows(kept)
        return removed

    def count_samples_per_letter(self) -> Dict[str, int]:
        counts = {L: 0 for L in self.letters}
        if not os.path.isfile(self.samples_csv):
            return counts
        with open(self.samples_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                L = row.get("letter", "").strip().upper()
                if L in counts:
                    counts[L] += 1
        return counts
