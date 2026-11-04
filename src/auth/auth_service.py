# auth_service.py
# Servicio de autenticacion: registro e inicio de sesion.
# Responsabilidad unica: validar credenciales y delegar en la base de datos.
# Paradigma: capa de logica de negocio, bajo acoplamiento con GUI y DB.

from typing import Optional, Tuple

from src.config import LEARNING_LANGUAGES
from src.database import DatabaseManager, User
from src.languages import normalize_language, t


class AuthService:
    """
    Gestiona registro e inicio de sesion.
    Valida reglas de negocio antes de llamar al DatabaseManager.
    """

    def __init__(self, db_manager: DatabaseManager) -> None:
        self._db = db_manager

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
    ) -> Tuple[bool, str]:
        """
        Registra un usuario tras validar formato y coincidencia de contrasenas.
        Retorna (exito, mensaje).
        """
        # Los mensajes salen en el idioma que la persona eligio para aprender.
        lang = normalize_language(learning_language)
        ok, msg = self.validate_registration(username, password, confirm_password, lang)
        if not ok:
            return False, msg
        if learning_language not in LEARNING_LANGUAGES:
            return False, t(lang, "invalid_language")
        return self._db.register_user(
            username,
            password,
            color_blind_mode=color_blind_mode,
            accessible_reading_mode=accessible_reading_mode,
            dyslexia_spacing_mode=dyslexia_spacing_mode,
            reading_font_size=reading_font_size,
            learning_language=learning_language,
        )

    def validate_registration(
        self,
        username: str,
        password: str,
        confirm_password: str,
        language: str = "es",
    ) -> Tuple[bool, str]:
        """
        Valida el primer paso del registro (formato, contrasenas y usuario
        disponible) antes de pasar a elegir idioma y accesibilidad.
        Retorna (valido, mensaje).
        """
        lang = normalize_language(language)
        msg = self._validate_credentials(username, password, lang)
        if msg:
            return False, msg
        if password != confirm_password:
            return False, t(lang, "passwords_mismatch")
        if self._db.user_exists(username):
            return False, t(lang, "username_taken")
        return True, ""

    def _validate_credentials(self, username: str, password: str, language: str = "es") -> str:
        """Valida longitud y caracteres. Retorna mensaje de error o cadena vacia."""
        from src.config import MIN_USERNAME_LENGTH, MAX_USERNAME_LENGTH, MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH
        username = username.strip()
        if len(username) < MIN_USERNAME_LENGTH:
            return t(language, "username_short", n=MIN_USERNAME_LENGTH)
        if len(username) > MAX_USERNAME_LENGTH:
            return t(language, "username_long", n=MAX_USERNAME_LENGTH)
        if len(password) < MIN_PASSWORD_LENGTH:
            return t(language, "password_short", n=MIN_PASSWORD_LENGTH)
        if len(password) > MAX_PASSWORD_LENGTH:
            return t(language, "password_long", n=MAX_PASSWORD_LENGTH)
        if not any(c.isupper() for c in password):
            return t(language, "password_no_upper")
        # Caracter especial: cualquier simbolo que no sea letra, numero ni espacio.
        if not any(not c.isalnum() and not c.isspace() for c in password):
            return t(language, "password_no_special")
        return ""

    def login(self, username: str, password: str) -> Optional[User]:
        """
        Valida credenciales y retorna el User si el login es correcto.
        """
        if not username or not password:
            return None
        return self._db.authenticate(username.strip(), password)
