# review_ai.py
# Asistente de retroalimentacion inteligente para el modo REPASO.
#
# Este modulo NO reimplementa MediaPipe ni el clasificador de senas: solo
# interpreta la informacion que el proyecto ya calcula en cada frame
# (letra objetivo, letra detectada, confianza, FingerState de
# `finger_analyzer.py` y/o el vector de features de `feature_extractor.py`)
# para explicarle al usuario, en lenguaje natural, que esta fallando en su
# seña y como corregirla.
#
# Es multilingue: recibe un AIContext (src/languages/ai_context.py) con el
# idioma, la lengua de senas, el alfabeto, la letra, sus instrucciones y el
# modulo. Responde en el idioma del perfil y evalua con las reglas del
# alfabeto seleccionado (LSC, ASL o LIBRAS), nunca con las de otro.
#
# Uso tipico (dentro del backend, por ejemplo en main.py):
#
#   from src.sign_language.review_ai import ReviewAI
#
#   review_ai = ReviewAI("en")
#   feedback = review_ai.analyze(
#       target_letter="V",
#       detected_letter="U",
#       confidence=0.81,
#       finger_state=finger_state,          # FingerState ya calculado por FingerAnalyzer
#       features=extract_features(landmarks),  # opcional, vector/():dict de feature_extractor
#       landmarks=landmarks,                # opcional, para revisar encuadre
#   )
#   feedback.as_dict()
#   # {"correct": False, "title": "U / V confusion",
#   #  "message": "You are signing a U: your index and middle fingers are too close together.", ...}

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from src.languages import MODULE_REVIEW, AIContext, build_ai_context, t
from src.languages.sign_alphabets import (
    CHECK_BK_THUMB,
    CHECK_MN_THUMB_COVER,
    CHECK_TS_THUMB,
    CHECK_UV_SEPARATION,
)

from .feature_extractor import features_to_dict

# ---------------------------------------------------------------------------
# Utilidades genericas para leer datos que pueden llegar como FingerState
# (dataclass), dict o None, sin acoplarse a un tipo concreto.
# ---------------------------------------------------------------------------


def _get(obj: Any, name: str, default: Any = None) -> Any:
    """Lee un atributo tanto de un dataclass (FingerState) como de un dict."""
    if obj is None:
        return default
    if isinstance(obj, Mapping):
        return obj.get(name, default)
    return getattr(obj, name, default)


FINGER_KEYS: Tuple[str, ...] = ("thumb", "index", "middle", "ring", "pinky")


def _finger_pattern(finger_state: Any) -> Optional[Tuple[bool, bool, bool, bool, bool]]:
    """Extrae (thumb, index, middle, ring, pinky) de un FingerState o dict."""
    if finger_state is None:
        return None
    values = [_get(finger_state, key) for key in FINGER_KEYS]
    if any(v is None for v in values):
        return None
    return tuple(bool(v) for v in values)  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Categorias de retroalimentacion
# ---------------------------------------------------------------------------

CATEGORY_FINGERS = "dedos"
CATEGORY_ORIENTATION = "orientacion"
CATEGORY_POSITION = "posicion_general"
CATEGORY_CORRECT = "correcto"


@dataclass(frozen=True)
class ReviewFeedback:
    """Resultado estructurado del analisis de un intento en modo Repaso."""

    correct: bool
    category: str
    title: str
    message: str
    tip: str
    target_letter: str
    detected_letter: Optional[str]
    confidence: Optional[float] = None
    confusion_pair: bool = False
    details: Tuple[str, ...] = field(default_factory=tuple)
    language: str = "es"
    sign_language: str = "LSC"
    module: str = MODULE_REVIEW
    instructions: Optional[str] = None

    def as_dict(self) -> dict:
        return {
            "correct": self.correct,
            "category": self.category,
            "title": self.title,
            "message": self.message,
            "tip": self.tip,
            "target_letter": self.target_letter,
            "detected_letter": self.detected_letter,
            "confidence": self.confidence,
            "confusion_pair": self.confusion_pair,
            "details": list(self.details),
            "language": self.language,
            "sign_language": self.sign_language,
            "module": self.module,
            "instructions": self.instructions,
        }


# ---------------------------------------------------------------------------
# ReviewAI: motor de analisis
# ---------------------------------------------------------------------------


class ReviewAI:
    """
    Analiza un intento confirmado del modo Repaso y devuelve retroalimentacion
    estructurada y accionable, sin depender de la interfaz ni de la base de
    datos (igual que LearningPerformanceAnalyzer).

    Las instrucciones de cada letra, los patrones de dedos, las confusiones
    conocidas y las reglas de orientacion se toman del alfabeto del idioma
    (src/languages/sign_alphabets.py): LSC para "es", ASL para "en" y LIBRAS
    para "pt". Los textos se generan en el idioma del perfil.
    """

    def __init__(self, language: str = "es", module: str = MODULE_REVIEW) -> None:
        self._context: AIContext = build_ai_context(language, module)
        self.language = self._context.language
        self._rules = self._context.rules

    @property
    def context(self) -> AIContext:
        return self._context

    # Atajos de texto ---------------------------------------------------
    def _t(self, key: str, **kwargs) -> str:
        return t(self.language, key, **kwargs)

    def _finger_name(self, key: str) -> str:
        return self._t(f"finger_{key}")

    def _hint(self, letter: str) -> Optional[str]:
        return self._rules.describe(letter)

    def _feedback(self, **kwargs) -> ReviewFeedback:
        target = kwargs.get("target_letter", "")
        return ReviewFeedback(
            language=self.language,
            sign_language=self._context.sign_language,
            module=self._context.module,
            instructions=self._hint(target) if target else None,
            **kwargs,
        )

    # -------------------------------------------------------------------

    def analyze(
        self,
        target_letter: str,
        detected_letter: Optional[str],
        confidence: Optional[float] = None,
        finger_state: Any = None,
        features: Any = None,
        landmarks: Optional[Sequence[Any]] = None,
    ) -> ReviewFeedback:
        target = (target_letter or "").strip().upper()
        detected = (detected_letter or "").strip().upper() or None

        feat = self._normalize_features(features)

        # 1) Sin deteccion clara: no hay seña que analizar.
        if detected is None:
            return self._no_detection_feedback(target, confidence)

        # 2) Acierto.
        if detected == target:
            return self._correct_feedback(target, confidence)

        # 3) Confusion conocida entre letras del alfabeto activo.
        confusion = self._match_known_confusion(target, detected, finger_state, feat)
        if confusion is not None:
            return confusion

        # 4) Diferencia de patron de dedos contra la letra objetivo.
        finger_feedback = self._finger_pattern_feedback(target, detected, confidence, finger_state)
        if finger_feedback is not None:
            return finger_feedback

        # 5) Orientacion de la mano/palma.
        orientation_feedback = self._orientation_feedback(target, detected, confidence, finger_state)
        if orientation_feedback is not None:
            return orientation_feedback

        # 6) Posicion general de la mano en el encuadre.
        position_feedback = self._general_position_feedback(
            target, detected, confidence, finger_state, feat, landmarks
        )
        if position_feedback is not None:
            return position_feedback

        # 7) Fallback generico: no se pudo aislar una causa especifica.
        return self._generic_feedback(target, detected, confidence)

    def analyze_attempts(self, attempts: Sequence[Mapping[str, Any]]) -> ReviewFeedback:
        """Compara intentos confirmados de Repaso y destaca el error repetido.

        Cada intento se analiza primero con :meth:`analyze`, por lo que este
        metodo conserva las mismas reglas de dedos, orientacion, posicion y
        confusiones del analisis individual. No clasifica ni calcula features
        nuevos; solo encuentra el diagnostico que mas se repite.
        """
        analyzed: List[ReviewFeedback] = []
        for attempt in attempts:
            if not isinstance(attempt, Mapping):
                continue
            analyzed.append(
                self.analyze(
                    target_letter=str(attempt.get("target_letter", "")),
                    detected_letter=attempt.get("detected_letter"),
                    confidence=attempt.get("confidence"),
                    finger_state=attempt.get("finger_state"),
                    features=attempt.get("features"),
                    landmarks=attempt.get("landmarks"),
                )
            )

        if not analyzed:
            return self._comparative_generic_feedback("", None, None, 0)

        # Los aciertos no son errores a priorizar. Si todos fueron correctos,
        # se conserva el feedback positivo del ultimo intento.
        incorrect = [feedback for feedback in analyzed if not feedback.correct]
        if not incorrect:
            return self._with_comparison_details(analyzed[-1], len(analyzed), "correcto")

        groups: Dict[Tuple[str, str], List[ReviewFeedback]] = {}
        for feedback in incorrect:
            error_key = self._comparison_error_key(feedback)
            if error_key is None:
                continue
            groups.setdefault(error_key, []).append(feedback)

        if groups:
            repeated_key, repeated_feedback = max(groups.items(), key=lambda item: len(item[1]))
            # Un solo caso no demuestra un patron: evita atribuir una causa
            # especifica cuando los cinco errores fueron distintos.
            if len(repeated_feedback) >= 2:
                return self._with_comparison_details(repeated_feedback[-1], len(analyzed), repeated_key[1])

        last = incorrect[-1]
        return self._comparative_generic_feedback(
            last.target_letter,
            last.detected_letter,
            last.confidence,
            len(analyzed),
        )

    @staticmethod
    def _comparison_error_key(feedback: ReviewFeedback) -> Optional[Tuple[str, str]]:
        """Devuelve una clave de causa ya diagnosticada por el analisis base."""
        if feedback.confusion_pair:
            return ("confusion", f"{feedback.detected_letter}/{feedback.target_letter}")

        if feedback.category == CATEGORY_FINGERS:
            # Los detalles de _finger_pattern_feedback contienen la primera
            # diferencia concreta, por ejemplo ``index: deberia ...``.
            for detail in feedback.details:
                if ": deberia" in detail:
                    return ("dedo", detail.split(":", 1)[0])
            return None

        if feedback.category == CATEGORY_ORIENTATION:
            for detail in feedback.details:
                if detail.startswith("palm_orientation="):
                    return ("orientacion", detail)
            return None

        if feedback.category == CATEGORY_POSITION:
            for detail in feedback.details:
                if detail == "hand_near_frame_edge":
                    return ("posicion", detail)
                if detail.startswith("fist_compactness="):
                    return ("posicion", feedback.title)
        return None

    @staticmethod
    def _with_comparison_details(
        feedback: ReviewFeedback, attempts_analyzed: int, repeated_error: str
    ) -> ReviewFeedback:
        return ReviewFeedback(
            correct=feedback.correct,
            category=feedback.category,
            title=feedback.title,
            message=feedback.message,
            tip=feedback.tip,
            target_letter=feedback.target_letter,
            detected_letter=feedback.detected_letter,
            confidence=feedback.confidence,
            confusion_pair=feedback.confusion_pair,
            details=feedback.details + (
                f"attempts_analyzed={attempts_analyzed}",
                f"repeated_error={repeated_error}",
            ),
            language=feedback.language,
            sign_language=feedback.sign_language,
            module=feedback.module,
            instructions=feedback.instructions,
        )

    def _reference_tip(self, target: str) -> Tuple[str, str]:
        """(texto para anadir al mensaje, tip) usando las instrucciones del alfabeto."""
        hint = self._hint(target)
        if not hint:
            return "", self._t("tip_compare_reference")
        return (
            self._t("reference_hint", letter=target, sign_language=self._context.sign_language, hint=hint),
            self._t("tip_with_hint", letter=target, hint=hint),
        )

    def _comparative_generic_feedback(
        self,
        target: str,
        detected: Optional[str],
        confidence: Optional[float],
        attempts_analyzed: int,
    ) -> ReviewFeedback:
        extra, tip = self._reference_tip(target)
        return self._feedback(
            correct=False,
            category=CATEGORY_FINGERS,
            title=self._t("comparative_title"),
            message=self._t("comparative_message") + extra,
            tip=tip,
            target_letter=target,
            detected_letter=detected,
            confidence=confidence,
            details=(
                f"attempts_analyzed={attempts_analyzed}",
                "repeated_error=none",
            ),
        )

    # ------------------------------------------------------------------
    # Casos base
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_features(features: Any) -> Dict[str, float]:
        if features is None:
            return {}
        if isinstance(features, Mapping):
            return dict(features)
        try:
            return features_to_dict(features)
        except Exception:
            return {}

    def _no_detection_feedback(self, target: str, confidence: Optional[float]) -> ReviewFeedback:
        return self._feedback(
            correct=False,
            category=CATEGORY_POSITION,
            title=self._t("no_detection_title"),
            message=self._t("no_detection_message"),
            tip=self._t("no_detection_tip"),
            target_letter=target,
            detected_letter=None,
            confidence=confidence,
        )

    def _correct_feedback(self, target: str, confidence: Optional[float]) -> ReviewFeedback:
        extra = ""
        if confidence is not None and confidence < 0.7:
            extra = self._t("correct_low_conf")
        return self._feedback(
            correct=True,
            category=CATEGORY_CORRECT,
            title=self._t("correct_title"),
            message=self._t("correct_message", letter=target, sign_language=self._context.sign_language) + extra,
            tip=self._t("correct_tip"),
            target_letter=target,
            detected_letter=target,
            confidence=confidence,
        )

    # ------------------------------------------------------------------
    # Confusiones conocidas (propias de cada alfabeto)
    # ------------------------------------------------------------------

    def _match_known_confusion(
        self,
        target: str,
        detected: str,
        finger_state: Any = None,
        features: Optional[Mapping[str, float]] = None,
    ) -> Optional[ReviewFeedback]:
        for group in self._rules.confusable_groups:
            if target in group and detected in group:
                explanation = self._known_confusion_explanation(target, detected, finger_state, features or {})
                if explanation is not None:
                    message, tip, detail = explanation
                else:
                    # La letra detectada por si sola no demuestra que rasgo
                    # geometrico esta fallando. No se inventa una causa.
                    extra, tip = self._reference_tip(target)
                    message = self._t("confusion_unknown", detected=detected) + extra
                    detail = "confusion_difference=not_available"
                return self._feedback(
                    correct=False,
                    category=CATEGORY_FINGERS,
                    title=self._t("confusion_title", detected=detected, target=target),
                    message=message,
                    tip=tip,
                    target_letter=target,
                    detected_letter=detected,
                    confusion_pair=True,
                    details=(f"grupo_confusion={'/'.join(sorted(group))}", detail),
                )
        return None

    def _known_confusion_explanation(
        self,
        target: str,
        detected: str,
        finger_state: Any,
        features: Mapping[str, float],
    ) -> Optional[Tuple[str, str, str]]:
        """Explica solo diferencias que los rasgos actuales pueden comprobar
        y que son validas en el alfabeto activo (confusion_checks)."""
        checks = self._rules.confusion_checks
        two_finger_pose = _get(finger_state, "two_finger_pose")
        thumb_between = _get(finger_state, "thumb_between")
        four_fingers_up = _get(finger_state, "four_fingers_up")
        ring = _get(finger_state, "ring")
        pinky = _get(finger_state, "pinky")
        thumb_cover_count = _get(finger_state, "thumb_cover_count")

        separation = features.get("index_middle_sep")
        try:
            separation = float(separation) if separation is not None else None
        except (TypeError, ValueError):
            separation = None

        # U/V (ASL y LIBRAS: U = indice y medio juntos, V = separados).
        if CHECK_UV_SEPARATION in checks:
            fingers_together = two_finger_pose == "together_up" or (separation is not None and separation < 0.22)
            fingers_apart = two_finger_pose == "apart_up" or (separation is not None and separation > 0.32)
            if target == "V" and detected == "U" and fingers_together:
                return self._t("uv_together_msg"), self._t("uv_together_tip"), "confusion_difference=index_middle_together"
            if target == "U" and detected == "V" and fingers_apart:
                return self._t("uv_apart_msg"), self._t("uv_apart_tip"), "confusion_difference=index_middle_apart"

        # B/K (ASL): cuatro dedos extendidos y pulgar entre indice y medio.
        if CHECK_BK_THUMB in checks:
            if target == "B" and detected == "K":
                if thumb_between is True:
                    return self._t("bk_thumb_between_msg"), self._t("bk_thumb_between_tip"), "confusion_difference=thumb_between"
                if ring is False or pinky is False:
                    return self._t("bk_four_up_msg"), self._t("bk_four_up_tip"), "confusion_difference=four_fingers_up"
            if target == "K" and detected == "B":
                if four_fingers_up is True:
                    return self._t("kb_four_up_msg"), self._t("kb_four_up_tip"), "confusion_difference=four_fingers_up"
                if thumb_between is False:
                    return self._t("kb_thumb_msg"), self._t("kb_thumb_tip"), "confusion_difference=thumb_not_between"

        # M/N (ASL): cuantos dedos cubre el pulgar.
        if CHECK_MN_THUMB_COVER in checks and isinstance(thumb_cover_count, int):
            if target == "M" and detected == "N" and thumb_cover_count < 3:
                return self._t("mn_low_msg"), self._t("mn_low_tip"), "confusion_difference=thumb_cover_count_low"
            if target == "N" and detected == "M" and thumb_cover_count >= 3:
                return self._t("nm_high_msg"), self._t("nm_high_tip"), "confusion_difference=thumb_cover_count_high"

        # T/S (ASL): la T lleva el pulgar entre indice y medio.
        if CHECK_TS_THUMB in checks:
            if target == "T" and detected == "S" and thumb_between is False:
                return self._t("ts_msg"), self._t("ts_tip"), "confusion_difference=thumb_not_between"
            if target == "S" and detected == "T" and thumb_between is True:
                return self._t("st_msg"), self._t("st_tip"), "confusion_difference=thumb_between"

        return None

    # ------------------------------------------------------------------
    # Posicion / forma de los dedos
    # ------------------------------------------------------------------

    def _finger_pattern_feedback(
        self,
        target: str,
        detected: str,
        confidence: Optional[float],
        finger_state: Any,
    ) -> Optional[ReviewFeedback]:
        expected = self._rules.expected_fingers.get(target)
        current = _finger_pattern(finger_state)
        if expected is None or current is None:
            return None

        mismatches: List[str] = []
        detail_list: List[str] = []
        first_key: Optional[str] = None
        for key, expected_val, actual_val in zip(FINGER_KEYS, expected, current):
            if expected_val == actual_val:
                continue
            if first_key is None:
                first_key = key
            name = self._finger_name(key)
            if expected_val and not actual_val:
                if key == "index" and _get(finger_state, "index_bent"):
                    mismatches.append(self._t("finger_too_bent", finger=name))
                else:
                    mismatches.append(self._t("finger_not_extended", finger=name))
                detail_list.append(f"{key}: deberia estar extendido")
            else:
                mismatches.append(self._t("finger_should_bend", finger=name))
                detail_list.append(f"{key}: deberia estar flexionado")

        if not mismatches or first_key is None:
            return None

        message = " ".join(mismatches[:2])
        should_extend = expected[FINGER_KEYS.index(first_key)]
        tip = self._t(
            "tip_extend_finger" if should_extend else "tip_bend_finger",
            finger=self._finger_name(first_key),
        )

        return self._feedback(
            correct=False,
            category=CATEGORY_FINGERS,
            title=self._t("fingers_title"),
            message=message,
            tip=tip,
            target_letter=target,
            detected_letter=detected,
            confidence=confidence,
            details=tuple(detail_list),
        )

    # ------------------------------------------------------------------
    # Orientacion de la mano
    # ------------------------------------------------------------------

    def _orientation_feedback(
        self,
        target: str,
        detected: str,
        confidence: Optional[float],
        finger_state: Any,
    ) -> Optional[ReviewFeedback]:
        palm_orientation = _get(finger_state, "palm_orientation")
        if not palm_orientation or target in self._rules.orientation_free_letters:
            return None

        expects_lateral = target in self._rules.lateral_letters
        sign_language = self._context.sign_language

        if palm_orientation in ("down", "lateral") and not expects_lateral:
            prefix = "orient_down" if palm_orientation == "down" else "orient_lateral"
            return self._feedback(
                correct=False,
                category=CATEGORY_ORIENTATION,
                title=self._t(f"{prefix}_title"),
                message=self._t(f"{prefix}_msg", letter=target, sign_language=sign_language),
                tip=self._t(f"{prefix}_tip"),
                target_letter=target,
                detected_letter=detected,
                confidence=confidence,
                details=(f"palm_orientation={palm_orientation}",),
            )

        if palm_orientation == "frontal" and expects_lateral:
            return self._feedback(
                correct=False,
                category=CATEGORY_ORIENTATION,
                title=self._t("orient_frontal_title"),
                message=self._t("orient_frontal_msg", letter=target, sign_language=sign_language),
                tip=self._t("orient_frontal_tip"),
                target_letter=target,
                detected_letter=detected,
                confidence=confidence,
                details=("palm_orientation=frontal",),
            )

        return None

    # ------------------------------------------------------------------
    # Posicion general de la mano (encuadre / cercania a la camara)
    # ------------------------------------------------------------------

    def _general_position_feedback(
        self,
        target: str,
        detected: str,
        confidence: Optional[float],
        finger_state: Any,
        features: Dict[str, float],
        landmarks: Optional[Sequence[Any]],
    ) -> Optional[ReviewFeedback]:
        if self._hand_near_frame_edge(landmarks):
            return self._feedback(
                correct=False,
                category=CATEGORY_POSITION,
                title=self._t("edge_title"),
                message=self._t("edge_msg"),
                tip=self._t("edge_tip"),
                target_letter=target,
                detected_letter=detected,
                confidence=confidence,
                details=("hand_near_frame_edge",),
            )

        fist_compact = features.get("fist_compactness") if features else None
        if fist_compact is not None:
            if fist_compact < 0.55 or fist_compact > 1.6:
                prefix = "small" if fist_compact < 0.55 else "big"
                return self._feedback(
                    correct=False,
                    category=CATEGORY_POSITION,
                    title=self._t(f"{prefix}_title"),
                    message=self._t(f"{prefix}_msg"),
                    tip=self._t(f"{prefix}_tip"),
                    target_letter=target,
                    detected_letter=detected,
                    confidence=confidence,
                    details=(f"fist_compactness={fist_compact:.2f}",),
                )

        return None

    @staticmethod
    def _hand_near_frame_edge(landmarks: Optional[Sequence[Any]]) -> bool:
        if not landmarks:
            return False
        try:
            xs = [float(_get(lm, "x")) for lm in landmarks]
            ys = [float(_get(lm, "y")) for lm in landmarks]
        except Exception:
            return False
        if not xs or not ys:
            return False
        margin = 0.04
        return min(xs) < margin or max(xs) > 1.0 - margin or min(ys) < margin or max(ys) > 1.0 - margin

    # ------------------------------------------------------------------
    # Fallback
    # ------------------------------------------------------------------

    def _generic_feedback(self, target: str, detected: str, confidence: Optional[float]) -> ReviewFeedback:
        hint = self._hint(target)
        return self._feedback(
            correct=False,
            category=CATEGORY_FINGERS,
            title=self._t("generic_title"),
            message=self._t("generic_msg", detected=detected, target=target),
            tip=self._t("tip_with_hint", letter=target, hint=hint) if hint else self._t("generic_tip", target=target),
            target_letter=target,
            detected_letter=detected,
            confidence=confidence,
        )


# ---------------------------------------------------------------------------
# Funcion de conveniencia a nivel de modulo (mismo patron que
# performance_analyzer.py, para poder usarla sin instanciar la clase).
# ---------------------------------------------------------------------------


def analyze_review_attempt(
    target_letter: str,
    detected_letter: Optional[str],
    confidence: Optional[float] = None,
    finger_state: Any = None,
    features: Any = None,
    landmarks: Optional[Sequence[Any]] = None,
    language: str = "es",
) -> Dict[str, Any]:
    """Atajo funcional: analiza un intento y devuelve un dict listo para JSON."""
    feedback = ReviewAI(language).analyze(
        target_letter=target_letter,
        detected_letter=detected_letter,
        confidence=confidence,
        finger_state=finger_state,
        features=features,
        landmarks=landmarks,
    )
    return feedback.as_dict()
