# web_api.py
# API llamada desde JS (pywebview.api.*)

import base64
from typing import Any, Dict, List, Optional


class WebAPI:
    def __init__(self, controller: Any) -> None:
        self._c = controller
        self._last_msg_idx = 0

    # ===== Auth =====
    def login(self, username: str, password: str, ui_language: Optional[str] = None) -> Dict[str, Any]:
        ok, msg = self._c.web_login(username, password, ui_language)
        return {"ok": ok, "msg": msg}

    def register(
        self,
        username: str,
        password: str,
        confirm_password: str,
        color_blind_mode: bool = False,
        accessible_reading_mode: bool = False,
        dyslexia_spacing_mode: bool = False,
        reading_font_size: str = "medium",
        learning_language: str = "es",
    ) -> Dict[str, Any]:
        ok, msg = self._c.web_register(
            username,
            password,
            confirm_password,
            color_blind_mode,
            accessible_reading_mode,
            dyslexia_spacing_mode,
            reading_font_size,
            learning_language,
        )
        return {"ok": ok, "msg": msg}

    def logout(self) -> Dict[str, Any]:
        self._c.web_logout()
        self._last_msg_idx = 0
        return {"ok": True}

    def set_color_blind_mode(self, enabled: bool) -> Dict[str, Any]:
        return self._c.web_set_color_blind_mode(enabled)

    def set_accessibility_preferences(
        self,
        color_blind_mode: bool,
        accessible_reading_mode: bool,
        night_mode: bool = False,
        dyslexia_spacing_mode: bool = False,
        reading_font_size: str = "medium",
    ) -> Dict[str, Any]:
        return self._c.web_set_accessibility_preferences(
            color_blind_mode,
            accessible_reading_mode,
            night_mode,
            dyslexia_spacing_mode,
            reading_font_size,
        )

    def set_learning_language(self, language: str) -> Dict[str, Any]:
        return self._c.web_set_learning_language(language)

    def get_language_pack(self, language: Optional[str] = None) -> Dict[str, Any]:
        return self._c.web_get_language_pack(language)

    # ===== Voice =====
    def voice_start(self) -> Dict[str, Any]:
        self._c.on_voice_start_capture()
        return {"ok": True}

    def voice_stop(self) -> Dict[str, Any]:
        self._c.on_voice_stop_capture()
        return {"ok": True}

    # ===== Texto a voz (respaldo con voces SAPI de Windows) =====
    def speak(self, text: str, locale: Optional[str] = None) -> Dict[str, Any]:
        return self._c.web_speak(text, locale)

    def stop_speaking(self) -> Dict[str, Any]:
        return self._c.web_stop_speaking()

    # ===== Signs buffer =====
    def sign_space(self) -> Dict[str, Any]:
        self._c.on_sign_space()
        return {"ok": True}

    def sign_backspace(self) -> Dict[str, Any]:
        self._c.on_sign_backspace()
        return {"ok": True}

    def sign_clear(self) -> Dict[str, Any]:
        self._c.on_sign_clear()
        return {"ok": True}

    def sign_accept(self) -> Dict[str, Any]:
        self._c.on_sign_accept()
        return {"ok": True}

    def sign_send(self) -> Dict[str, Any]:
        self._c.on_sign_send()
        return {"ok": True}

    # ===== Reto: deletrear nombre =====
    def challenge_start(self, mode: str = "name") -> Dict[str, Any]:
        self._c.on_challenge_start(mode)
        return {"ok": True}

    def challenge_stop(self) -> Dict[str, Any]:
        self._c.on_challenge_stop()
        return {"ok": True}

    def challenge_keep_practicing(self) -> Dict[str, Any]:
        return self._c.on_challenge_keep_practicing()

    def challenge_next_letter(self) -> Dict[str, Any]:
        return self._c.on_challenge_next_letter()

    # ===== Desempeno de aprendizaje =====
    def learning_attempt(self, target_letter: str, detected_letter: str) -> Dict[str, Any]:
        return self._c.web_learning_attempt(target_letter, detected_letter)

    def review_attempt(self, target_letter: str, detected_letter: str) -> Dict[str, Any]:
        return self._c.web_review_attempt(target_letter, detected_letter)

    def reset_review_attempts(self) -> Dict[str, Any]:
        return self._c.web_reset_review_attempts()

    def learning_performance(self, letter: str) -> Dict[str, Any]:
        return self._c.web_learning_performance(letter)

    def get_favorite_letters(self) -> Dict[str, Any]:
        return self._c.web_get_favorite_letters()

    def set_favorite_letter(self, letter: str, is_favorite: bool) -> Dict[str, Any]:
        return self._c.web_set_favorite_letter(letter, is_favorite)

    # ===== Evaluacion WEB =====
    def eval_start(self, duration_seconds: int) -> Dict[str, Any]:
        return self._c.web_start_evaluation(duration_seconds)

    def eval_stop(self) -> Dict[str, Any]:
        return self._c.web_stop_evaluation()

    # ===== Poll =====
    def get_state(self, consume_messages: bool = True) -> Dict[str, Any]:
        # Solo el poll principal del chat consume los mensajes nuevos; otras
        # consultas (racha, reto) pasan False para no "robarlos" del chat.
        st = self._c.get_web_state()
        msgs = st.get("messages", [])
        new_msgs = msgs[self._last_msg_idx :]
        if consume_messages:
            self._last_msg_idx = len(msgs)
        st = dict(st)
        st["new_messages"] = new_msgs if consume_messages else []
        return st

