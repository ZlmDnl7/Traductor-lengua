# main.py
# Control principal: coordina autenticacion, navegacion y modulo de traduccion.
# Paradigma: orquestador, inyeccion de dependencias, bajo acoplamiento.

import sys
import os
import threading
import queue
import traceback
from typing import Optional
import base64
import copy
import time
import random

# Asegurar que el directorio raiz del proyecto esta en el path
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from src.database import DatabaseManager
from src.auth import AuthService
from src.gui import App
from src.camera import CameraCapture
from src.image_processing import HandDetector
from src.sign_language import (
    FingerAnalyzer,
    LearningPerformanceAnalyzer,
    MotionDetector,
    ReviewAI,
    SignClassifier,
    spell_text,
)
from src.config import DEFAULT_LEARNING_LANGUAGE, USE_WEB_UI
from src.languages import (
    MODULE_CHALLENGE,
    MODULE_REVIEW,
    get_profile,
    language_pack,
    normalize_language,
    t,
)


class MainController:
    """
    Controlador principal: enlaza GUI, autenticacion, base de datos
    y modulo de traduccion (camara + deteccion + clasificacion).
    """

    def __init__(self) -> None:
        self._db = DatabaseManager()
        self._auth = AuthService(self._db)
        self._db.init_database()

        self._app: App = None
        self._current_user = None
        self._login_screen = None
        self._register_screen = None
        self._translation_screen = None
        self._interaction_screen = None
        self._aprendizaje_screen = None
        self._voice_screen = None
        self._voice_recording = False
        self._voice_stop_event: Optional[threading.Event] = None
        self._voice_thread: Optional[threading.Thread] = None
        self._sign_buffer = ""
        self._last_appended_letter: Optional[str] = None
        self._lm_smooth: Optional[list] = None

        # Modulo de traduccion (creado al abrir la pantalla)
        self._camera: CameraCapture = None
        self._hand_detector: HandDetector = None
        self._sign_classifier: SignClassifier = None
        # Deteccion de movimiento para J y Z (el modelo ML solo ve una postura estatica).
        self._finger_analyzer: FingerAnalyzer = None
        self._motion_detector: MotionDetector = None
        self._translation_running = False
        self._after_id = None
        self._read_fail_count = 0
        self._MAX_READ_FAILS_BEFORE_MESSAGE = 45
        self._camera_error: Optional[str] = None

        # Threading para que la GUI no se congele
        self._translation_thread: Optional[threading.Thread] = None
        self._stop_translation_event: Optional[threading.Event] = None
        self._translation_queue: Optional["queue.Queue[tuple]"] = None

        # ===== Estado UI Web (PyWebView) =====
        self._web_api = None
        self._web_messages = []  # {"who": str, "text": str}
        self._web_frame_b64: Optional[str] = None
        self._web_letter: Optional[str] = None
        self._web_finger_state= None
        self._web_confidence:float = 0.0
        self._web_landmarks= None
        self._web_features = None
        self._web_last_frame_ts = 0.0
        # Estados y errores se guardan como claves de traduccion (src/languages/messages.py)
        # y se traducen al idioma activo al enviarlos a la UI.
        self._voice_status = "voice_status_ready"
        self._voice_error = ""
        self._voice_language = DEFAULT_LEARNING_LANGUAGE
        self._study_streak = {"current_streak": 0, "best_streak": 0, "last_study_date": None}
        self._web_color_blind_mode = False
        self._web_accessible_reading_mode = False
        self._web_dyslexia_spacing_mode = False
        self._web_reading_font_size = "medium"
        self._web_night_mode = False
        self._web_learning_language = DEFAULT_LEARNING_LANGUAGE
        self._learning_performance = LearningPerformanceAnalyzer(DEFAULT_LEARNING_LANGUAGE)
        self._review_ai = ReviewAI(DEFAULT_LEARNING_LANGUAGE, MODULE_REVIEW)
        self._challenge_ai = ReviewAI(DEFAULT_LEARNING_LANGUAGE, MODULE_CHALLENGE)
        # Historial efimero: solo conserva los intentos confirmados de la
        # letra actual en Repaso; nunca se persiste en MongoDB.
        self._review_attempts: list[dict] = []
        
        # ===== Reto: deletrear el nombre de usuario o una palabra =====
        self._challenge_mode: str = "name"
        self._challenge_word: str = ""
        self._challenge_skipped: list = []
        self._challenge_feedback: Optional[dict] = None
        self._challenge_wrong_letter: Optional[str] = None
        self._challenge_wrong_count: int = 0
        self._challenge_feedback_frames: int = 12  # frames con la letra equivocada antes de pedir ayuda a la IA
        self._challenge_letters: list = []
        self._challenge_index: int = 0
        self._challenge_done: bool = False
        self._challenge_active: bool = False
        self._challenge_match_count: int = 0
        self._challenge_hold_frames: int = 10  # frames consecutivos para confirmar cada letra
        # Tras confirmar una letra se muestra "Correcto" ~1 s antes de avanzar.
        self._challenge_advance_delay_s: float = 1.0
        self._challenge_confirmed_at: Optional[float] = None
        # Letra recien confirmada: se ignora hasta que la mano cambie o se retire,
        # asi una misma seña sostenida no confirma tambien la letra siguiente (p. ej. "ANNA").
        self._challenge_release_letter: Optional[str] = None
        self._challenge_lock = threading.Lock()
        # Intentos equivocados confirmados en la letra actual. Al llegar al limite
        # el reto se pausa y la IA pregunta si guardar la letra para Repaso y si
        # seguir con ella o pasar a la siguiente.
        self._challenge_errors_to_prompt: int = 4
        self._challenge_error_count: int = 0
        self._challenge_error_prompt: bool = False
        # Posiciones que la persona decidio pasar sin completarlas.
        self._challenge_passed: list = []
        # Ultima deteccion recibida (tambien durante la pausa), para no contar la
        # sena que siga en camara al responder la pregunta de la IA.
        self._challenge_last_letter: Optional[str] = None

        # ===== Estado de evaluacion WEB =====
        self._evaluation_active = False
        self._evaluation_duration = 0
        self._evaluation_deadline = 0.0
        self._evaluation_score = 0
        self._evaluation_hits = 0
        self._evaluation_errors = 0
        self._evaluation_target: Optional[str] = None
        self._evaluation_detected: Optional[str] = None
        self._evaluation_hit_letters: list[str] = []
        self._evaluation_error_letters: list[str] = []
        self._evaluation_last_detected: Optional[str] = None
        self._evaluation_same_streak = 0
        self._evaluation_hold_frames = 3

    # ====== Idioma ======
    def _t(self, key: str, **kwargs) -> str:
        return t(self._web_learning_language, key, **kwargs)

    def _translate_stored(self, value) -> str:
        """Traduce una clave guardada (str o (clave, kwargs)) al idioma activo."""
        if not value:
            return ""
        if isinstance(value, tuple):
            key, kwargs = value
            return self._t(key, **kwargs)
        return self._t(value)

    def set_current_login_screen(self, screen) -> None:
        self._login_screen = screen

    def set_current_register_screen(self, screen) -> None:
        self._register_screen = screen

    def set_translation_screen(self, screen) -> None:
        self._translation_screen = screen
        self._start_translation_loop()

    def set_interaction_screen(self, screen) -> None:
        self._interaction_screen = screen
        self._translation_screen = screen
        self._start_translation_loop()
        self._sync_sign_buffer()

    def set_aprendizaje_screen(self, screen) -> None:
        self._aprendizaje_screen = screen
        self._translation_screen = screen
        self._start_translation_loop()

    def on_login(self, username: str, password: str) -> None:
        user = self._auth.login(username, password)
        if user is None:
            if self._login_screen:
                self._login_screen.show_error(self._t("login_failed"))
            return
        self._current_user = user
        self._study_streak = self._db.get_study_streak(user.username)
        self._app.show_main_menu(user.username)

    def on_go_register(self) -> None:
        if self._login_screen:
            self._login_screen.clear_error()
        self._app.show_register()

    def on_go_login(self) -> None:
        if self._register_screen:
            self._register_screen.clear_error()
        self._app.show_login()

    def on_register(self, username: str, password: str, confirm_password: str) -> None:
        ok, msg = self._auth.register(username, password, confirm_password)
        if not ok:
            if self._register_screen:
                self._register_screen.show_error(msg)
            return
        if self._register_screen:
            self._register_screen.clear_error()
        self._app.show_login()

    def on_logout(self) -> None:
        self._current_user = None
        self._study_streak = {"current_streak": 0, "best_streak": 0, "last_study_date": None}
        self._review_attempts.clear()
        if not USE_WEB_UI:
            self._app.show_login()

    def on_open_translation(self) -> None:
        self._app.show_translation()

    def on_open_voice(self) -> None:
        self._app.show_voice()

    def on_open_interaction(self) -> None:
        if USE_WEB_UI:
            self._ensure_translation_running()
        else:
            self._app.show_interaction()

    def on_open_aprendizaje(self) -> None:
        if not USE_WEB_UI:
            self._app.show_aprendizaje()

    def on_interaction_back(self) -> None:
        self._stop_translation_loop()
        self._release_translation_resources()
        self._interaction_screen = None
        if not USE_WEB_UI:
            self._app.show_main_menu(self._current_user.username)

    def on_aprendizaje_back(self) -> None:
        self._stop_translation_loop()
        self._release_translation_resources()
        self._aprendizaje_screen = None
        if not USE_WEB_UI:
            self._app.show_main_menu(self._current_user.username)

    def on_app_close(self) -> None:
        """Cierre limpio de la app (evita crash de MediaPipe en background)."""
        try:
            self.web_stop_speaking()
        except Exception:
            pass
        try:
            self._voice_stop_event.set() if self._voice_stop_event is not None else None
        except Exception:
            pass
        try:
            self._stop_translation_loop()
            self._release_translation_resources()
        except Exception:
            pass
        try:
            if self._app:
                self._app.quit()
        except Exception:
            pass

    # ====== Helpers para ejecutar "en UI" ======
    def _post_to_ui(self, fn) -> None:
        if USE_WEB_UI:
            fn()
            return
        try:
            if self._app and self._app.get_root():
                self._app.get_root().after(0, fn)
            else:
                fn()
        except Exception:
            fn()

    # ====== Web API ======
    def get_web_api(self):
        if self._web_api is None:
            from src.gui_web.web_api import WebAPI
            self._web_api = WebAPI(self)
        return self._web_api

    def web_login(self, username: str, password: str, ui_language: Optional[str] = None):
        user = self._auth.login(username, password)
        if user is None:
            # Antes de iniciar sesion se usa el idioma que muestra la interfaz.
            return False, t(normalize_language(ui_language or self._web_learning_language), "login_failed")
        self._current_user = user
        self._study_streak = self._db.get_study_streak(user.username)
        self._web_color_blind_mode = self._db.get_color_blind_mode(user.username)
        self._web_accessible_reading_mode = self._db.get_accessible_reading_mode(user.username)
        self._web_dyslexia_spacing_mode = self._db.get_dyslexia_spacing_mode(user.username)
        self._web_reading_font_size = self._db.get_reading_font_size(user.username)
        self._web_night_mode = self._db.get_night_mode(user.username)
        self._apply_learning_language(self._db.get_learning_language(user.username))
        self._ensure_translation_running()
        return True, "OK"

    def web_register(
        self,
        username: str,
        password: str,
        confirm_password: str,
        color_blind_mode: bool = False,
        accessible_reading_mode: bool = False,
        dyslexia_spacing_mode: bool = False,
        reading_font_size: str = "medium",
        learning_language: str = "es",
    ):
        return self._auth.register(
            username,
            password,
            confirm_password,
            color_blind_mode,
            accessible_reading_mode,
            dyslexia_spacing_mode,
            reading_font_size,
            learning_language,
        )

    def web_logout(self) -> None:
        self._current_user = None
        self._web_color_blind_mode = False
        self._web_accessible_reading_mode = False
        self._web_dyslexia_spacing_mode = False
        self._web_reading_font_size = "medium"
        self._web_night_mode = False
        self._apply_learning_language(DEFAULT_LEARNING_LANGUAGE)
        self._study_streak = {"current_streak": 0, "best_streak": 0, "last_study_date": None}
        self._review_attempts.clear()
        self._stop_translation_loop()
        self._release_translation_resources()
        self._web_messages.clear()
        self._sign_buffer = ""
        self._web_frame_b64 = None
        self._web_letter = None                             # <-- LÍNEA NUEVA
        self._web_landmarks = None 
        self._web_features = None
        self._web_last_frame_ts = 0.0
        self._voice_status = "voice_status_ready"
        self._voice_error = ""
        self._reset_challenge_state()
        self._challenge_letters = []
        self._challenge_index = 0
        self._challenge_done = False
        self._challenge_active = False
        self._challenge_match_count = 0
        self._camera_error = None
        self._reset_evaluation_state()

    def web_set_color_blind_mode(self, enabled: bool) -> dict:
        result = self.web_set_accessibility_preferences(
            enabled,
            self._web_accessible_reading_mode,
            self._web_night_mode,
            self._web_dyslexia_spacing_mode,
            self._web_reading_font_size,
        )
        if not result.get("ok"):
            return {"ok": False, "msg": result.get("msg", self._t("must_login")), "enabled": False}
        return {"ok": True, "enabled": result["color_blind_mode"]}

    def web_set_accessibility_preferences(
        self,
        color_blind_mode: bool,
        accessible_reading_mode: bool,
        night_mode: bool = False,
        dyslexia_spacing_mode: bool = False,
        reading_font_size: str = "medium",
    ) -> dict:
        if self._current_user is None:
            return {
                "ok": False,
                "msg": self._t("must_login"),
                "color_blind_mode": False,
                "accessible_reading_mode": False,
                "night_mode": False,
            }
        try:
            preferences = self._db.set_accessibility_preferences(
                self._current_user.username,
                color_blind_mode=bool(color_blind_mode),
                accessible_reading_mode=bool(accessible_reading_mode),
                night_mode=bool(night_mode),
                dyslexia_spacing_mode=bool(dyslexia_spacing_mode),
                reading_font_size=reading_font_size,
            )
        except ValueError:
            return {"ok": False, "msg": self._t("invalid_font_size")}
        self._web_color_blind_mode = preferences["color_blind_mode"]
        self._web_accessible_reading_mode = preferences["accessible_reading_mode"]
        self._web_dyslexia_spacing_mode = preferences["dyslexia_spacing_mode"]
        self._web_reading_font_size = preferences["reading_font_size"]
        self._web_night_mode = preferences["night_mode"]
        return {"ok": True, **preferences}

    def web_set_learning_language(self, language: str) -> dict:
        if self._current_user is None:
            return {"ok": False, "msg": t(normalize_language(language), "must_login")}
        try:
            language = self._db.set_learning_language(self._current_user.username, language)
        except ValueError:
            return {"ok": False, "msg": self._t("invalid_language")}
        self._apply_learning_language(language)
        return {"ok": True, "learning_language": language, "language_pack": language_pack(language)}

    def web_get_language_pack(self, language: Optional[str] = None) -> dict:
        """Perfil del idioma (voz, alfabeto, imagenes, instrucciones de cada sena)."""
        return {"ok": True, "language_pack": language_pack(language or self._web_learning_language)}

    def _apply_learning_language(self, language: str) -> None:
        """
        Cambia TODO lo que depende del idioma: alfabeto y modelo de senas
        (es = LSC, en = ASL, pt = LIBRAS), IA de Repaso y de Reto, mensajes,
        idioma de voz, reto y evaluacion en curso. Si la camara ya esta
        corriendo, el modelo se cambia en vivo. No queda configuracion del
        idioma anterior.
        """
        language = normalize_language(language)
        changed = language != self._web_learning_language
        self._web_learning_language = language
        if not changed:
            return
        self._learning_performance = LearningPerformanceAnalyzer(language)
        self._review_ai = ReviewAI(language, MODULE_REVIEW)
        self._challenge_ai = ReviewAI(language, MODULE_CHALLENGE)
        self._review_attempts.clear()
        self._web_letter = None
        self.web_stop_speaking()
        if self._sign_classifier is not None:
            self._sign_classifier = SignClassifier(language=language)
            if self._motion_detector is not None:
                self._motion_detector.reset()
            if not self._sign_classifier.is_trained():
                print(f"[Senas] Modelo '{language}' no entrenado. Ejecute: python collect_sign_samples.py --lang {language}")
        # Un reto o una evaluacion en curso continuan con el alfabeto nuevo.
        if self._challenge_letters:
            self._build_challenge(self._challenge_mode, keep_active=self._challenge_active)
        if self._evaluation_active:
            self._evaluation_target = self._random_evaluation_letter()
            self._evaluation_last_detected = None
            self._evaluation_same_streak = 0

    def web_speak(self, text: str, locale: Optional[str] = None) -> dict:
        """
        Texto a voz de respaldo (voces SAPI de Windows) cuando WebView2 no tiene
        una voz del idioma. Por defecto usa el locale del idioma activo.
        """
        from src.speech import text_to_speech

        return text_to_speech.speak(text, locale or get_profile(self._web_learning_language).speech_locale)

    def web_stop_speaking(self) -> dict:
        from src.speech import text_to_speech

        text_to_speech.stop()
        return {"ok": True}

    def _recognizable_letters(self) -> list:
        """
        Letras del alfabeto activo que el reconocimiento puede producir: clases
        entrenadas del modelo + letras detectadas por movimiento (p. ej. Ç en
        LIBRAS). Evita pedir letras imposibles (como la Ñ de LSC, sin muestras).
        """
        profile = get_profile(self._web_learning_language)
        known = self._sign_classifier.known_letters() if self._sign_classifier else set()
        if not known:
            return list(profile.model_alphabet)
        return [L for L in profile.model_alphabet if L in known or L in profile.motion_letters]

    def _random_evaluation_letter(self) -> str:
        return random.choice(self._recognizable_letters())

    def _reset_evaluation_state(self) -> None:
        self._evaluation_active = False
        self._evaluation_duration = 0
        self._evaluation_deadline = 0.0
        self._evaluation_score = 0
        self._evaluation_hits = 0
        self._evaluation_errors = 0
        self._evaluation_target = None
        self._evaluation_detected = None
        self._evaluation_hit_letters = []
        self._evaluation_error_letters = []
        self._evaluation_last_detected = None
        self._evaluation_same_streak = 0

    def web_start_evaluation(self, duration_seconds: int) -> dict:
        if self._current_user is None:
            return {"ok": False, "msg": self._t("must_login")}
        try:
            duration = int(duration_seconds)
        except (TypeError, ValueError):
            return {"ok": False, "msg": self._t("invalid_duration")}
        if duration <= 0:
            return {"ok": False, "msg": self._t("duration_positive")}

        self._reset_evaluation_state()
        self._evaluation_active = True
        self._evaluation_duration = duration
        self._evaluation_deadline = time.monotonic() + duration
        self._evaluation_target = self._random_evaluation_letter()
        self._ensure_translation_running()
        return {"ok": True, "duration_seconds": duration, "target_letter": self._evaluation_target}

    def web_stop_evaluation(self) -> dict:
        results = self._evaluation_results()
        self._evaluation_active = False
        return {"ok": True, "results": results}

    def _evaluation_results(self) -> dict:
        remaining = max(0, int(self._evaluation_deadline - time.monotonic())) if self._evaluation_active else 0
        elapsed = self._evaluation_duration - remaining
        return {
            "score": self._evaluation_score,
            "hits": self._evaluation_hits,
            "errors": self._evaluation_errors,
            "duration_seconds": self._evaluation_duration,
            "elapsed_seconds": max(0, min(self._evaluation_duration, elapsed)),
            "hit_letters": list(self._evaluation_hit_letters),
            "error_letters": list(self._evaluation_error_letters),
        }

    def _process_evaluation(self, detected_letter: Optional[str]) -> None:
        if not self._evaluation_active:
            return
        if time.monotonic() >= self._evaluation_deadline:
            self._evaluation_active = False
            return

        detected = (detected_letter or "").strip().upper()
        self._evaluation_detected = detected or None
        if not detected:
            self._evaluation_last_detected = None
            self._evaluation_same_streak = 0
            return
        if detected == self._evaluation_last_detected:
            self._evaluation_same_streak += 1
        else:
            self._evaluation_last_detected = detected
            self._evaluation_same_streak = 1
        if self._evaluation_same_streak < self._evaluation_hold_frames:
            return

        target = self._evaluation_target
        if detected == target:
            self._evaluation_score += 5
            self._evaluation_hits += 1
            self._evaluation_hit_letters.append(detected)
        else:
            self._evaluation_score -= 2
            self._evaluation_errors += 1
            self._evaluation_error_letters.append(target)
        self._evaluation_target = self._random_evaluation_letter()
        self._evaluation_last_detected = None
        self._evaluation_same_streak = 0

    def web_learning_attempt(self, target_letter: str, detected_letter: str) -> dict:
        """Registra un intento confirmado de APRENDIZAJE del usuario autenticado."""
        if self._current_user is None:
            return {"ok": False, "msg": self._t("must_login")}

        target, detected, error = self._validate_attempt(target_letter, detected_letter)
        if error:
            return error

        language = self._web_learning_language
        stats = self._db.record_learning_attempt(
            self._current_user.username,
            target,
            detected == target,
            language,
        )
        self._study_streak = self._db.get_study_streak(self._current_user.username)
        analysis = self._learning_performance.analyze(stats, target, language)
        return {
            "ok": True,
            "letter": target,
            "analysis": analysis.as_dict(),
            "study_streak": self._study_streak,
        }

    def _validate_attempt(self, target_letter: str, detected_letter: str):
        """Normaliza un intento y rechaza letras que no pertenecen al alfabeto activo
        (p. ej. una llamada pendiente hecha antes de cambiar de idioma)."""
        target = (target_letter or "").strip().upper()
        detected = (detected_letter or "").strip().upper()
        if not target or not detected:
            return target, detected, {"ok": False, "msg": self._t("invalid_attempt")}
        if target not in get_profile(self._web_learning_language).learning_alphabet:
            return target, detected, {"ok": False, "msg": self._t("invalid_letter")}
        return target, detected, None

    def web_review_attempt(self, target_letter: str, detected_letter: str) -> dict:
        """Registra un intento del modo REPASO y devuelve retroalimentación de la IA."""
        if self._current_user is None:
            return {"ok": False, "msg": self._t("must_login")}

        target, detected, error = self._validate_attempt(target_letter, detected_letter)
        if error:
            return error

        # Reutiliza el mismo contador de 5 intentos que ya usa Aprendizaje.
        language = self._web_learning_language
        stats = self._db.record_learning_attempt(
            self._current_user.username,
            target,
            detected == target,
            language,
        )
        self._study_streak = self._db.get_study_streak(self._current_user.username)
        analysis = self._learning_performance.analyze(stats, target, language)

        # Un cambio de letra inicia una nueva sesion de Repaso. Las copias
        # profundas evitan que los datos del frame siguiente alteren intentos
        # ya confirmados. Solo se guardan como maximo los cinco intentos.
        if self._review_attempts and self._review_attempts[0]["target_letter"] != target:
            self._review_attempts.clear()
        if len(self._review_attempts) < 5:
            self._review_attempts.append(
                {
                    "target_letter": target,
                    "detected_letter": detected,
                    "confidence": float(self._web_confidence or 0.0),
                    "finger_state": copy.deepcopy(self._web_finger_state),
                    "features": copy.deepcopy(self._web_features),
                    "landmarks": copy.deepcopy(self._web_landmarks),
                }
            )

        # Un acierto siempre debe reemplazar una correccion previa, incluso
        # si ya se completo el analisis de cinco intentos.
        if detected == target:
            feedback = self._review_ai.analyze(
                target_letter=target,
                detected_letter=detected,
                confidence=self._web_confidence,
                finger_state=self._web_finger_state,
                features=self._web_features,
                landmarks=self._web_landmarks,
            )
        elif len(self._review_attempts) == 5:
            feedback = self._review_ai.analyze_attempts(self._review_attempts)
        else:
            feedback = self._review_ai.analyze(
                target_letter=target,
                detected_letter=detected,
                confidence=self._web_confidence,
                finger_state=self._web_finger_state,
                features=self._web_features,
                landmarks=self._web_landmarks,
            )

        return {
            "ok": True,
            "letter": target,
            "analysis": analysis.as_dict(),
            "feedback": feedback.as_dict(),
            "review_attempt": len(self._review_attempts),
            "review_attempt_limit": 5,
            "review_analysis_ready": len(self._review_attempts) == 5,
            "study_streak": self._study_streak,
        }

    def web_reset_review_attempts(self) -> dict:
        """Descarta el historial temporal al salir o reiniciar Repaso."""
        self._review_attempts.clear()
        return {"ok": True}

    def web_learning_performance(self, letter: str) -> dict:
        """Devuelve el analisis actual de una letra para el asistente de APRENDIZAJE."""
        if self._current_user is None:
            return {"ok": False, "msg": self._t("must_login")}
        target = (letter or "").strip().upper()
        language = self._web_learning_language
        if not target or target not in get_profile(language).learning_alphabet:
            return {"ok": False, "msg": self._t("invalid_letter")}
        stats = self._db.get_learning_performance(self._current_user.username, target, language)
        analysis = self._learning_performance.analyze(stats, target, language)
        return {
            "ok": True,
            "letter": target,
            "analysis": analysis.as_dict(),
            "study_streak": self._study_streak,
        }

    def web_get_favorite_letters(self) -> dict:
        if self._current_user is None:
            return {"ok": False, "msg": self._t("must_login"), "letters": []}
        language = self._web_learning_language
        return {
            "ok": True,
            "language": language,
            "letters": self._db.get_favorite_letters(self._current_user.username, language),
        }

    def web_set_favorite_letter(self, letter: str, is_favorite: bool) -> dict:
        if self._current_user is None:
            return {"ok": False, "msg": self._t("must_login"), "letters": []}
        target = (letter or "").strip().upper()
        language = self._web_learning_language
        if not target or target not in get_profile(language).learning_alphabet:
            return {"ok": False, "msg": self._t("invalid_letter"), "letters": []}
        if is_favorite:
            letters = self._db.add_favorite_letter(self._current_user.username, target, language)
        else:
            letters = self._db.remove_favorite_letter(self._current_user.username, target, language)
        return {"ok": True, "language": language, "letters": letters}

    def get_web_state(self):
        self._finish_challenge_confirmation()
        challenge_progress = 0.0
        challenge_confirmed = self._challenge_confirmed_at is not None
        if self._challenge_letters and not self._challenge_done:
            challenge_progress = 1.0 if challenge_confirmed else self._challenge_match_count / float(self._challenge_hold_frames)
        evaluation_remaining = 0
        if self._evaluation_active:
            evaluation_remaining = max(0, int(self._evaluation_deadline - time.monotonic()))
            if evaluation_remaining == 0:
                self._evaluation_active = False
        language = self._web_learning_language if self._current_user else DEFAULT_LEARNING_LANGUAGE
        profile = get_profile(language)
        return {
            "logged_in": self._current_user is not None,
            "username": self._current_user.username if self._current_user else None,
            "color_blind_mode": self._web_color_blind_mode if self._current_user else False,
            "accessible_reading_mode": self._web_accessible_reading_mode if self._current_user else False,
            "dyslexia_spacing_mode": self._web_dyslexia_spacing_mode if self._current_user else False,
            "reading_font_size": self._web_reading_font_size if self._current_user else "medium",
            "night_mode": self._web_night_mode if self._current_user else False,
            "learning_language": language,
            "ui_locale": profile.ui_locale,
            "speech_locale": profile.speech_locale,
            "sign_language": profile.sign_language,
            "frame_jpeg_b64": self._web_frame_b64,
            "letter": self._web_letter,
            "sign_text": self._sign_buffer,
            "messages": list(self._web_messages),
            "voice_status": self._translate_stored(self._voice_status),
            "voice_error": self._translate_stored(self._voice_error),
            "voice_recording": self._voice_recording,
            "camera_error": self._translate_stored(self._camera_error),
            "challenge_mode": self._challenge_mode,
            "challenge_word": self._challenge_word,
            "challenge_skipped": list(self._challenge_skipped),
            "challenge_feedback": self._challenge_feedback,
            "challenge_letters": list(self._challenge_letters),
            "challenge_index": self._challenge_index,
            "challenge_done": self._challenge_done,
            "challenge_progress": min(1.0, challenge_progress),
            "challenge_confirmed": challenge_confirmed,
            "challenge_error_count": self._challenge_error_count,
            "challenge_error_prompt": self._challenge_error_prompt,
            "challenge_passed": list(self._challenge_passed),
            "recognizable_letters": self._recognizable_letters(),
            "study_streak": self._study_streak,
            "evaluation_active": self._evaluation_active,
            "evaluation_remaining": evaluation_remaining,
            "evaluation_duration": self._evaluation_duration,
            "evaluation_score": self._evaluation_score,
            "evaluation_hits": self._evaluation_hits,
            "evaluation_errors": self._evaluation_errors,
            "evaluation_target": self._evaluation_target,
            "evaluation_detected": self._evaluation_detected,
        }

    # ====== Reto: deletrear el nombre de usuario o una palabra ======
    def _reset_challenge_state(self) -> None:
        self._challenge_mode = "name"
        self._challenge_word = ""
        self._challenge_skipped = []
        self._challenge_feedback = None
        self._challenge_wrong_letter = None
        self._challenge_wrong_count = 0
        self._challenge_confirmed_at = None
        self._challenge_release_letter = None
        self._challenge_error_count = 0
        self._challenge_error_prompt = False
        self._challenge_passed = []

    def _pick_challenge_word(self) -> str:
        words = [w for w in get_profile(self._web_learning_language).challenge_words if w != self._challenge_word]
        return random.choice(words) if words else ""

    def _build_challenge(self, mode: str, keep_active: bool = True) -> None:
        """
        Prepara el reto en el alfabeto activo. Los caracteres que el alfabeto o
        el modelo no admiten se descartan (y se informan) para que el reto nunca
        quede bloqueado esperando una letra imposible.
        """
        language = self._web_learning_language
        mode = "word" if mode == "word" else "name"
        if mode == "word":
            text = self._pick_challenge_word()
        else:
            text = self._current_user.username if self._current_user else ""
        letters, skipped = spell_text(text, language, allowed=self._recognizable_letters())
        self._challenge_mode = mode
        self._challenge_word = text
        self._challenge_skipped = skipped
        self._challenge_letters = letters
        self._challenge_index = 0
        self._challenge_done = False
        self._challenge_match_count = 0
        self._challenge_feedback = None
        self._challenge_wrong_letter = None
        self._challenge_wrong_count = 0
        self._challenge_confirmed_at = None
        self._challenge_release_letter = None
        self._challenge_error_count = 0
        self._challenge_error_prompt = False
        self._challenge_passed = []
        self._challenge_active = keep_active

    def on_challenge_start(self, mode: str = "name") -> None:
        """Arranca (o reinicia) el reto: deletrear el nombre del usuario o una palabra del idioma."""
        self._build_challenge(mode, keep_active=True)

    def on_challenge_stop(self) -> None:
        """El usuario salio de la pantalla de reto (no hace falta seguir comparando letras)."""
        self._challenge_active = False

    def _clear_challenge_error_state_locked(self, release_letter: Optional[str]) -> None:
        # La sena que siga en camara no cuenta hasta que la mano cambie o se retire.
        self._challenge_release_letter = release_letter
        self._challenge_wrong_letter = None
        self._challenge_wrong_count = 0
        self._challenge_match_count = 0
        self._challenge_error_count = 0
        self._challenge_error_prompt = False

    def on_challenge_keep_practicing(self) -> dict:
        """Respuesta a la pregunta de la IA: seguir con la misma letra."""
        with self._challenge_lock:
            last = self._challenge_last_letter
            target = self._challenge_letters[self._challenge_index] if self._challenge_letters and not self._challenge_done else None
            self._clear_challenge_error_state_locked(last if last != target else None)
        return {"ok": True}

    def on_challenge_next_letter(self) -> dict:
        """Respuesta a la pregunta de la IA: pasar a la letra siguiente sin completarla."""
        with self._challenge_lock:
            if not self._challenge_letters or self._challenge_done:
                return {"ok": False}
            self._clear_challenge_error_state_locked(self._challenge_last_letter)
            self._challenge_feedback = None
            self._challenge_confirmed_at = None
            self._challenge_passed.append(self._challenge_index)
            self._challenge_index += 1
            if self._challenge_index >= len(self._challenge_letters):
                self._challenge_done = True
        return {"ok": True}

    def _advance_challenge(self, letter: Optional[str]) -> None:
        """
        Compara la letra detectada con la letra objetivo actual del reto.
        Requiere sostener la seña correcta varios frames seguidos; al confirmarla
        la UI muestra "Correcto" y ~1 s despues se avanza a la letra siguiente.
        """
        with self._challenge_lock:
            self._challenge_last_letter = letter
            if not self._challenge_letters or self._challenge_done:
                return
            if self._challenge_confirmed_at is not None:
                # Confirmacion en curso: ninguna deteccion cuenta hasta avanzar.
                self._finish_challenge_confirmation_locked()
                return
            if self._challenge_error_prompt:
                # La IA espera la decision de la persona.
                return
            if self._challenge_release_letter is not None:
                if letter == self._challenge_release_letter:
                    return
                self._challenge_release_letter = None
            target = self._challenge_letters[self._challenge_index]
            if letter != target:
                self._challenge_match_count = 0
                self._track_challenge_mistake(target, letter)
                return
            self._challenge_wrong_letter = None
            self._challenge_wrong_count = 0
            self._challenge_match_count += 1
            if self._challenge_match_count < self._challenge_hold_frames:
                return
            self._challenge_feedback = None
            self._challenge_confirmed_at = time.monotonic()

    def _finish_challenge_confirmation(self) -> None:
        with self._challenge_lock:
            self._finish_challenge_confirmation_locked()

    def _finish_challenge_confirmation_locked(self) -> None:
        """Avanza UNA sola vez cuando termina la pausa de confirmacion."""
        if self._challenge_confirmed_at is None:
            return
        if time.monotonic() - self._challenge_confirmed_at < self._challenge_advance_delay_s:
            return
        self._challenge_release_letter = self._challenge_letters[self._challenge_index]
        self._challenge_confirmed_at = None
        self._challenge_match_count = 0
        self._challenge_index += 1
        if self._challenge_index >= len(self._challenge_letters):
            self._challenge_done = True

    def _track_challenge_mistake(self, target: str, letter: Optional[str]) -> None:
        """
        Si la persona sostiene una letra equivocada, la IA (con las reglas del
        alfabeto activo y en su idioma) explica como corregirla.
        """
        if not letter:
            self._challenge_wrong_letter = None
            self._challenge_wrong_count = 0
            return
        if letter == self._challenge_wrong_letter:
            self._challenge_wrong_count += 1
        else:
            self._challenge_wrong_letter = letter
            self._challenge_wrong_count = 1
        # Un intento equivocado se confirma igual que uno correcto (varios frames
        # seguidos) y cuenta una sola vez mientras la misma sena siga en camara.
        if self._challenge_wrong_count == self._challenge_hold_frames:
            self._challenge_error_count += 1
            if self._challenge_error_count >= self._challenge_errors_to_prompt:
                self._challenge_error_prompt = True
                return
        if self._challenge_wrong_count != self._challenge_feedback_frames:
            return
        feedback = self._challenge_ai.analyze(
            target_letter=target,
            detected_letter=letter,
            confidence=self._web_confidence,
            finger_state=self._web_finger_state,
            features=self._web_features,
            landmarks=self._web_landmarks,
        )
        self._challenge_feedback = feedback.as_dict()

    # ====== Buffer de señas ======
    def _sync_sign_buffer(self) -> None:
        if self._interaction_screen is not None:
            self._interaction_screen.set_sign_text(self._sign_buffer)

    def on_sign_clear(self) -> None:
        self._sign_buffer = ""
        self._last_appended_letter = None
        self._sync_sign_buffer()

    def on_sign_space(self) -> None:
        self._sign_buffer += " "
        self._last_appended_letter = None
        self._sync_sign_buffer()

    def on_sign_backspace(self) -> None:
        if self._sign_buffer:
            self._sign_buffer = self._sign_buffer[:-1]
        self._last_appended_letter = None
        self._sync_sign_buffer()

    def on_sign_accept(self) -> None:
        """Agrega la letra actualmente detectada al buffer (confirmacion manual)."""
        letter = self._web_letter
        if letter:
            self._sign_buffer += letter
            self._sync_sign_buffer()

    def on_sign_send(self) -> None:
        """Envia el texto armado por senas al chat y limpia el buffer."""
        text = (self._sign_buffer or "").strip()
        if not text:
            return
        who = self._t("chat_signs")
        if self._interaction_screen is not None:
            self._interaction_screen.append_chat(who, text)
        # "kind" permite a la UI mostrar la etiqueta en el idioma activo.
        self._web_messages.append({
            "who": who,
            "kind": "signs",
            "text": text,
            "language": self._web_learning_language,
            "speech_locale": get_profile(self._web_learning_language).speech_locale,
        })
        self.on_sign_clear()

    def set_voice_screen(self, screen) -> None:
        self._voice_screen = screen

    def on_voice_back(self) -> None:
        self._voice_screen = None
        self._app.show_main_menu(self._current_user.username)

    def on_voice_start_capture(self) -> None:
        if self._voice_recording:
            return
        if self._voice_thread is not None and self._voice_thread.is_alive():
            self._voice_error = "mic_busy"
            return
        self._voice_recording = True
        self._voice_status = "voice_status_recording"
        self._voice_error = ""
        # Se transcribe en el idioma activo al empezar a grabar.
        self._voice_language = self._web_learning_language
        self._voice_stop_event = threading.Event()
        thread = threading.Thread(
            target=self._voice_stream_worker,
            name="voice-stream-worker",
            daemon=True,
        )
        self._voice_thread = thread
        thread.start()

    def on_voice_stop_capture(self) -> None:
        if self._voice_stop_event is not None:
            self._voice_stop_event.set()
        self._voice_status = "voice_status_transcribing"
        if self._voice_screen is not None:
            self._voice_screen.set_transcribing(True)

    def _voice_stream_worker(self) -> None:
        err_key = None
        text = None
        language = self._voice_language
        try:
            from src.speech.voice_transcriber import VoiceInputError, record_until_stop, transcribe
            ev = self._voice_stop_event
            if ev is None:
                raise RuntimeError("Estado de grabacion invalido")
            try:
                audio = record_until_stop(ev)
            except VoiceInputError as e:
                err_key = e.code
                raise
            try:
                text = transcribe(audio, language) if audio.size > 0 else ""
            except Exception as e:
                err_key = ("speech_model_error", {"error": str(e)})
                raise
        except Exception:
            print(traceback.format_exc())
            err_key = err_key or "mic_error_generic"
        if isinstance(err_key, tuple):
            err_msg = t(language, err_key[0], **err_key[1])
        else:
            err_msg = t(language, err_key) if err_key else None

        def finish() -> None:
            self._voice_recording = False
            self._voice_stop_event = None
            self._voice_thread = None
            if self._voice_screen is not None:
                self._voice_screen.set_transcribing(False)
                self._voice_screen.reset_after_session()
                if err_msg:
                    self._voice_screen.show_error(err_msg)
                else:
                    self._voice_screen.set_result(text or "")
            if self._interaction_screen is not None:
                self._interaction_screen.voice_done()
                if err_msg:
                    self._interaction_screen.voice_error(err_msg)
                else:
                    if text and text.strip():
                        self._interaction_screen.append_chat(t(language, "chat_voice"), text)
                    else:
                        self._interaction_screen.voice_error(t(language, "voice_repeat"))
            self._voice_status = "voice_status_ready"
            if err_key:
                self._voice_error = err_key
            else:
                self._voice_error = ""
                if text and text.strip():
                    self._web_messages.append({
                        "who": t(language, "chat_voice"),
                        "kind": "voice",
                        "text": text.strip(),
                        "language": language,
                        "speech_locale": get_profile(language).speech_locale,
                    })
                else:
                    self._voice_error = "voice_repeat"

        self._post_to_ui(finish)

    def _ensure_translation_running(self) -> None:
        if self._translation_running:
            return
        self._start_translation_loop()

    def on_translation_back(self) -> None:
        self._stop_translation_loop()
        self._release_translation_resources()
        if not USE_WEB_UI:
            self._app.show_main_menu(self._current_user.username)

    def _start_translation_loop(self) -> None:
        """Inicializa camara, detectores y arranca el bucle de traduccion."""
        self._camera_error = None
        self._camera = CameraCapture()
        if not self._camera.open():
            self._camera_error = "camera_open_error"
            if self._translation_screen:
                self._translation_screen.show_camera_error()
            return
        for _ in range(15):
            self._camera.read()
        self._hand_detector = HandDetector()
        self._sign_classifier = SignClassifier(language=self._web_learning_language)
        self._finger_analyzer = FingerAnalyzer()
        self._motion_detector = MotionDetector()
        if not self._sign_classifier.is_trained():
            print(
                "[Senas] Modelo no entrenado. Ejecute: python collect_sign_samples.py"
                f" --lang {self._web_learning_language}"
            )
        self._translation_running = True
        self._read_fail_count = 0
        self._stop_translation_event = threading.Event()
        self._translation_queue = queue.Queue(maxsize=1)
        self._translation_thread = threading.Thread(
            target=self._translation_worker,
            name="translation-worker",
            daemon=True,
        )
        self._translation_thread.start()
        if not USE_WEB_UI:
            self._poll_translation_queue()

    def _translation_worker(self) -> None:
        assert self._translation_queue is not None
        assert self._stop_translation_event is not None
        while self._translation_running and not self._stop_translation_event.is_set():
            if not self._camera or not self._camera.is_opened():
                break
            ret, frame = self._camera.read()
            if not ret or frame is None:
                self._read_fail_count += 1
                if self._read_fail_count >= self._MAX_READ_FAILS_BEFORE_MESSAGE:
                    self._put_latest((None, None, "no_frames"))
                    self._camera_error = "camera_no_frames"
                continue

            self._read_fail_count = 0
            self._camera_error = None
            try:
                landmarks, frame_out = self._hand_detector.process(frame)
            except RuntimeError:
                break
            landmarks_classify = landmarks
            try:
                if landmarks is not None:
                    try:
                        from src.config import LANDMARK_SMOOTH_ALPHA, LANDMARK_SMOOTH_FOR_CLASSIFY
                        a = float(LANDMARK_SMOOTH_ALPHA)
                        smooth_classify = bool(LANDMARK_SMOOTH_FOR_CLASSIFY)
                    except Exception:
                        a = 0.65
                        smooth_classify = False
                    if self._lm_smooth is None or len(self._lm_smooth) != len(landmarks):
                        self._lm_smooth = [dict(lm) for lm in landmarks]
                    else:
                        for i in range(len(landmarks)):
                            cur = landmarks[i]
                            prev = self._lm_smooth[i]
                            prev["x"] = a * float(prev.get("x", 0.0)) + (1.0 - a) * float(cur.get("x", 0.0))
                            prev["y"] = a * float(prev.get("y", 0.0)) + (1.0 - a) * float(cur.get("y", 0.0))
                            prev["z"] = a * float(prev.get("z", 0.0)) + (1.0 - a) * float(cur.get("z", 0.0))
                    landmarks_draw = self._lm_smooth if a > 0 else landmarks
                    landmarks_classify = self._lm_smooth if smooth_classify else landmarks
                    self._hand_detector.draw_landmarks(frame_out, landmarks_draw)
                else:
                    self._lm_smooth = None

                letter, _conf = self._sign_classifier.letter_for_display(landmarks_classify)

                # J y Z son senas de MOVIMIENTO: el modelo ML solo ve una postura estatica
                # por frame y no puede distinguirlas de I / D en una sola imagen. Se rastrea
                # la trayectoria de la punta del dedo entre frames y, si calza con el gancho
                # de J o el zigzag de Z, se prioriza sobre la prediccion estatica del modelo.
                finger_state = self._finger_analyzer.analyze(landmarks_classify) if self._finger_analyzer else None
                self._web_finger_state = finger_state
                self._web_confidence= float(_conf or 0.0)
                self._web_landmarks=landmarks_classify
                self._web_features = self._sign_classifier.latest_features() if self._sign_classifier else None
                j_motion, z_motion = (
                    self._motion_detector.update(finger_state) if self._motion_detector else (False, False)
                )
                if finger_state is not None:
                    if j_motion and finger_state.pinky and not finger_state.index and not finger_state.middle:
                        letter = "J"
                    elif (
                        z_motion
                        and finger_state.index
                        and finger_state.index_up
                        and not finger_state.middle
                        and not finger_state.ring
                        and not finger_state.pinky
                    ):
                        letter = "Z"
                    elif (
                        letter == "C"
                        and self._web_learning_language == "pt"
                        and self._motion_detector is not None
                        and self._motion_detector.cedilla_motion
                    ):
                        # LIBRAS: la Ç es la forma de C con movimiento de la mano.
                        letter = "Ç"

                self._put_latest((frame_out, letter, "ok"))

                # Solo mostrar la letra detectada; el usuario confirma con "Aceptar".
                self._web_letter = letter

                self._process_evaluation(letter)

                if self._challenge_active:
                    self._advance_challenge(letter)
            except Exception:
                # Nunca dejar que un frame problematico mate el hilo de camara completo.
                print(traceback.format_exc())
                continue

            # Enviar frame a la UI web
            now = time.monotonic()
            try:
                from src.config import WEB_VIDEO_INTERVAL_MS, WEB_VIDEO_TARGET_WIDTH, WEB_VIDEO_JPEG_QUALITY
                interval_s = float(WEB_VIDEO_INTERVAL_MS) / 1000.0
                target_w = int(WEB_VIDEO_TARGET_WIDTH)
                jpeg_q = int(WEB_VIDEO_JPEG_QUALITY)
            except Exception:
                interval_s = 0.045
                target_w = 800
                jpeg_q = 55

            if now - self._web_last_frame_ts >= interval_s:
                self._web_last_frame_ts = now
                try:
                    import cv2
                    h, w = frame_out.shape[:2]
                    if w > target_w:
                        scale = float(target_w) / float(w)
                        frame_small = cv2.resize(frame_out, (int(w * scale), int(h * scale)))
                    else:
                        frame_small = frame_out
                    ok, buf = cv2.imencode(".jpg", frame_small, [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_q])
                    if ok:
                        self._web_frame_b64 = base64.b64encode(buf.tobytes()).decode("ascii")
                except Exception:
                    pass

    def _put_latest(self, item: tuple) -> None:
        if not self._translation_queue:
            return
        try:
            if self._translation_queue.full():
                try:
                    self._translation_queue.get_nowait()
                except queue.Empty:
                    pass
            self._translation_queue.put_nowait(item)
        except Exception:
            pass

    def _poll_translation_queue(self) -> None:
        if not self._translation_running or not self._translation_screen:
            return
        try:
            frame_out, letter, status = self._translation_queue.get_nowait() if self._translation_queue else (None, None, None)
            if status == "no_frames":
                self._translation_screen.show_no_frames_error()
            elif status == "ok":
                if frame_out is not None:
                    self._translation_screen.update_frame(frame_out)
                self._translation_screen.update_letter(letter)
                if self._interaction_screen is not None and letter:
                    if letter != self._last_appended_letter:
                        self._sign_buffer += letter
                        self._last_appended_letter = letter
                        self._sync_sign_buffer()
                self._web_letter = letter
                try:
                    import cv2
                    ok, buf = cv2.imencode(".jpg", frame_out, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
                    if ok:
                        self._web_frame_b64 = base64.b64encode(buf.tobytes()).decode("ascii")
                except Exception:
                    pass
        except queue.Empty:
            pass
        self._schedule_next()

    def _schedule_next(self) -> None:
        if USE_WEB_UI:
            return
        if self._translation_running and self._app:
            self._after_id = self._app.get_root().after(33, self._poll_translation_queue)

    def _stop_translation_loop(self) -> None:
        self._translation_running = False
        if self._stop_translation_event is not None:
            self._stop_translation_event.set()
        if not USE_WEB_UI:
            if self._app and self._after_id is not None:
                self._app.get_root().after_cancel(self._after_id)
                self._after_id = None
        if self._translation_thread is not None and self._translation_thread.is_alive():
            self._translation_thread.join(timeout=2.0)

    def _release_translation_resources(self) -> None:
        if self._camera:
            self._camera.release()
            self._camera = None
        if self._hand_detector:
            self._hand_detector.close()
            self._hand_detector = None
        self._translation_thread = None
        self._stop_translation_event = None
        self._translation_queue = None
        self._translation_screen = None
        self._aprendizaje_screen = None

    def run(self) -> None:
        """Punto de entrada: crea la GUI y arranca."""
        if USE_WEB_UI:
            from src.gui_web import WebApp
            self._app = WebApp(self)
            self._app.run()
        else:
            self._app = App(self)
            self._app.run()


def main() -> None:
    try:
        controller = MainController()
        controller.run()
    except RuntimeError as e:
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Error de base de datos", str(e))
            root.destroy()
        except Exception:
            pass
        raise


if __name__ == "__main__":
    main()
