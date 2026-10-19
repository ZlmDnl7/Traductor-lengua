# db_manager.py
# Gestion de base de datos MongoDB (local).
# Responsabilidad unica: operaciones CRUD y conexion.
# Paradigma: encapsulamiento, bajo acoplamiento.

import hashlib
import os
from datetime import date, timedelta
from typing import Optional, Tuple

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError

from src.config import (
    DEFAULT_LEARNING_LANGUAGE,
    LEARNING_LANGUAGES,
    MAX_ATTEMPTS,
    MONGO_DB_NAME,
    MONGO_URI,
    MONGO_USERS_COLLECTION,
)
from .models import User
from src.languages import normalize_language, t


class DatabaseManager:
    """
    Gestiona la conexion y operaciones sobre la base de datos.
    Implementa patron de responsabilidad unica para acceso a datos.
    """

    def __init__(self, mongo_uri: Optional[str] = None) -> None:
        # Permite override por variable de entorno, util para demos o laboratorios.
        env_uri = os.getenv("MONGO_URI")
        self._mongo_uri = (mongo_uri or env_uri or MONGO_URI).strip()
        self._client: Optional[MongoClient] = None

    def _get_client(self) -> MongoClient:
        if self._client is None:
            self._client = MongoClient(self._mongo_uri)
        return self._client

    def _users_collection(self):
        client = self._get_client()
        db = client[MONGO_DB_NAME]
        return db[MONGO_USERS_COLLECTION]

    def init_database(self) -> None:
        """
        Inicializa la coleccion e indices necesarios.
        En MongoDB la base se crea automaticamente al insertar el primer documento.
        """
        try:
            users = self._users_collection()
            # Username unico para evitar duplicados.
            users.create_index("username", unique=True)
        except Exception as e:
            raise RuntimeError(
                "No se pudo conectar a MongoDB. Verifique que el servicio de MongoDB este ejecutandose "
                "y que pueda conectarse a 'mongodb://localhost:27017' (o configure MONGO_URI)."
            ) from e

    @staticmethod
    def hash_password(password: str) -> str:
        """Genera hash SHA-256 de la contrasena."""
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def register_user(
        self,
        username: str,
        password: str,
        color_blind_mode: bool = False,
        accessible_reading_mode: bool = False,
        dyslexia_spacing_mode: bool = False,
        reading_font_size: str = "medium",
        learning_language: str = "es",
    ) -> Tuple[bool, str]:
        """
        Registra un nuevo usuario.
        Retorna (exito, mensaje).
        """
        lang = normalize_language(learning_language)
        if not username or not password:
            return False, t(lang, "register_required")
        username_clean = username.strip()
        try:
            password_hash = self.hash_password(password)
            users = self._users_collection()
            users.insert_one(
                {
                    "username": username_clean,
                    "password_hash": password_hash,
                    "learning_language": learning_language,
                    "accessibility": {
                        "color_blind_mode": bool(color_blind_mode),
                        "accessible_reading_mode": bool(accessible_reading_mode),
                        "dyslexia_spacing_mode": bool(dyslexia_spacing_mode),
                        "reading_font_size": self._normalize_reading_font_size(reading_font_size),
                    },
                }
            )
            return True, t(lang, "register_ok")
        except DuplicateKeyError:
            return False, t(lang, "username_taken")
        except PyMongoError as e:
            return False, t(lang, "register_error", error=str(e))

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """
        Valida credenciales y retorna el User si son correctas.
        """
        if not username or not password:
            return None
        password_hash = self.hash_password(password)
        users = self._users_collection()
        doc = users.find_one(
            {"username": username.strip(), "password_hash": password_hash},
            {"username": 1, "password_hash": 1},
        )
        if not doc:
            return None
        return User(id=str(doc.get("_id")), username=doc["username"], password_hash=doc["password_hash"])

    def user_exists(self, username: str) -> bool:
        """Comprueba si existe un usuario con el nombre dado."""
        users = self._users_collection()
        return users.count_documents({"username": username.strip()}, limit=1) > 0

    def get_color_blind_mode(self, username: str) -> bool:
        """Obtiene el modo daltónico guardado para un usuario."""
        username_clean = (username or "").strip()
        if not username_clean:
            return False
        users = self._users_collection()
        doc = users.find_one({"username": username_clean}, {"accessibility.color_blind_mode": 1}) or {}
        accessibility = doc.get("accessibility", {})
        return bool(accessibility.get("color_blind_mode", False))

    def set_color_blind_mode(self, username: str, enabled: bool) -> bool:
        """Actualiza únicamente el modo daltónico del usuario."""
        return self.set_accessibility_preferences(username, color_blind_mode=enabled)["color_blind_mode"]

    def get_accessible_reading_mode(self, username: str) -> bool:
        """Obtiene el modo de lectura accesible guardado para un usuario."""
        username_clean = (username or "").strip()
        if not username_clean:
            return False
        users = self._users_collection()
        doc = users.find_one({"username": username_clean}, {"accessibility.accessible_reading_mode": 1}) or {}
        accessibility = doc.get("accessibility", {})
        return bool(accessibility.get("accessible_reading_mode", False))

    def get_dyslexia_spacing_mode(self, username: str) -> bool:
        """Obtiene el espaciado adicional para lectura guardado."""
        username_clean = (username or "").strip()
        if not username_clean:
            return False
        users = self._users_collection()
        doc = users.find_one({"username": username_clean}, {"accessibility.dyslexia_spacing_mode": 1}) or {}
        accessibility = doc.get("accessibility", {})
        return bool(accessibility.get("dyslexia_spacing_mode", False))

    @staticmethod
    def _normalize_reading_font_size(value: str) -> str:
        return value if value in {"small", "medium", "large"} else "medium"

    def get_reading_font_size(self, username: str) -> str:
        """Obtiene el nivel de tamaño de texto guardado."""
        username_clean = (username or "").strip()
        if not username_clean:
            return "medium"
        users = self._users_collection()
        doc = users.find_one({"username": username_clean}, {"accessibility.reading_font_size": 1}) or {}
        accessibility = doc.get("accessibility", {})
        return self._normalize_reading_font_size(accessibility.get("reading_font_size", "medium"))

    def set_accessibility_preferences(
        self,
        username: str,
        color_blind_mode: Optional[bool] = None,
        accessible_reading_mode: Optional[bool] = None,
        night_mode: Optional[bool] = None,
        dyslexia_spacing_mode: Optional[bool] = None,
        reading_font_size: Optional[str] = None,
    ) -> dict:
        """Actualiza solo las preferencias de accesibilidad indicadas."""
        username_clean = (username or "").strip()
        if not username_clean:
            raise ValueError("El usuario es obligatorio")
        updates = {}
        if color_blind_mode is not None:
            updates["accessibility.color_blind_mode"] = bool(color_blind_mode)
        if accessible_reading_mode is not None:
            updates["accessibility.accessible_reading_mode"] = bool(accessible_reading_mode)
        if night_mode is not None:
            updates["accessibility.night_mode"] = bool(night_mode)
        if dyslexia_spacing_mode is not None:
            updates["accessibility.dyslexia_spacing_mode"] = bool(dyslexia_spacing_mode)
        if reading_font_size is not None:
            updates["accessibility.reading_font_size"] = self._normalize_reading_font_size(reading_font_size)
        if not updates:
            return {
                "color_blind_mode": self.get_color_blind_mode(username_clean),
                "accessible_reading_mode": self.get_accessible_reading_mode(username_clean),
                "night_mode": self.get_night_mode(username_clean),
                "dyslexia_spacing_mode": self.get_dyslexia_spacing_mode(username_clean),
                "reading_font_size": self.get_reading_font_size(username_clean),
            }
        users = self._users_collection()
        result = users.update_one(
            {"username": username_clean},
            {"$set": updates},
        )
        if result.matched_count != 1:
            raise ValueError("El usuario autenticado no existe")
        return {
            "color_blind_mode": self.get_color_blind_mode(username_clean),
            "accessible_reading_mode": self.get_accessible_reading_mode(username_clean),
            "night_mode": self.get_night_mode(username_clean),
            "dyslexia_spacing_mode": self.get_dyslexia_spacing_mode(username_clean),
            "reading_font_size": self.get_reading_font_size(username_clean),
        }

    def get_night_mode(self, username: str) -> bool:
        """Obtiene el modo noche guardado para un usuario."""
        username_clean = (username or "").strip()
        if not username_clean:
            return False
        users = self._users_collection()
        doc = users.find_one({"username": username_clean}, {"accessibility.night_mode": 1}) or {}
        accessibility = doc.get("accessibility", {})
        return bool(accessibility.get("night_mode", False))

    def get_learning_language(self, username: str) -> str:
        """Obtiene el idioma en el que el usuario aprende lenguaje de señas."""
        username_clean = (username or "").strip()
        if not username_clean:
            return DEFAULT_LEARNING_LANGUAGE
        users = self._users_collection()
        doc = users.find_one({"username": username_clean}, {"learning_language": 1}) or {}
        language = doc.get("learning_language")
        return language if language in LEARNING_LANGUAGES else DEFAULT_LEARNING_LANGUAGE

    def set_learning_language(self, username: str, language: str) -> str:
        """Actualiza el idioma de aprendizaje del usuario."""
        username_clean = (username or "").strip()
        if not username_clean:
            raise ValueError("El usuario es obligatorio")
        if language not in LEARNING_LANGUAGES:
            raise ValueError("Selecciona un idioma de aprendizaje valido")
        users = self._users_collection()
        result = users.update_one(
            {"username": username_clean},
            {"$set": {"learning_language": language}},
        )
        if result.matched_count != 1:
            raise ValueError("El usuario autenticado no existe")
        return language

    @staticmethod
    def _language_field(base: str, language: Optional[str]) -> str:
        """
        Campo por idioma de aprendizaje. Espanol (LSC) conserva los campos
        originales (learning_performance, favorite_letters) para no perder datos
        existentes; ASL y LIBRAS usan campos propios (p. ej. favorite_letters_en),
        asi una letra de un alfabeto nunca aparece en otro.
        """
        lang = language if language in LEARNING_LANGUAGES else DEFAULT_LEARNING_LANGUAGE
        return base if lang == DEFAULT_LEARNING_LANGUAGE else f"{base}_{lang}"

    def record_learning_attempt(self, username: str, letter: str, is_correct: bool, language: Optional[str] = None) -> dict:
        """Registra un intento confirmado de aprendizaje para un usuario, idioma y letra."""
        username_clean = (username or "").strip()
        letter_clean = (letter or "").strip().upper()
        if not username_clean or not letter_clean:
            raise ValueError("El usuario y la letra son obligatorios")

        performance_path = f"{self._language_field('learning_performance', language)}.{letter_clean}"
        field = f"{performance_path}.{'correct' if is_correct else 'incorrect'}"
        users = self._users_collection()
        result = users.update_one(
            {
                "username": username_clean,
                "$or": [
                    {f"{performance_path}.attempts": {"$lt": MAX_ATTEMPTS}},
                    {f"{performance_path}.attempts": {"$exists": False}},
                ],
            },
            {"$inc": {f"{performance_path}.attempts": 1, field: 1}},
        )
        if result.matched_count != 1 and not users.find_one({"username": username_clean}, {"_id": 1}):
            raise ValueError("El usuario autenticado no existe")
        self._record_study_day(username_clean)
        return self.get_learning_performance(username_clean, letter_clean, language)

    def _record_study_day(self, username: str) -> dict:
        """Actualiza la racha una sola vez por dia para el usuario."""
        users = self._users_collection()
        today = date.today()
        today_value = today.isoformat()
        doc = users.find_one(
            {"username": username},
            {"current_streak": 1, "best_streak": 1, "last_study_date": 1},
        ) or {}
        last_value = doc.get("last_study_date")
        current = max(0, int(doc.get("current_streak", 0)))
        best = max(0, int(doc.get("best_streak", 0)))

        if last_value == today_value:
            return {
                "current_streak": current,
                "best_streak": best,
                "last_study_date": today_value,
            }

        try:
            last_date = date.fromisoformat(str(last_value))
        except (TypeError, ValueError):
            last_date = None

        if last_date == today - timedelta(days=1):
            current += 1
        else:
            current = 1
        best = max(best, current)
        streak = {
            "current_streak": current,
            "best_streak": best,
            "last_study_date": today_value,
        }
        users.update_one({"username": username}, {"$set": streak})
        return streak

    def get_study_streak(self, username: str) -> dict:
        """Obtiene la racha persistida, sin registrar actividad."""
        users = self._users_collection()
        doc = users.find_one(
            {"username": (username or "").strip()},
            {"current_streak": 1, "best_streak": 1, "last_study_date": 1},
        ) or {}
        return {
            "current_streak": max(0, int(doc.get("current_streak", 0))),
            "best_streak": max(0, int(doc.get("best_streak", 0))),
            "last_study_date": doc.get("last_study_date"),
        }

    def get_learning_performance(self, username: str, letter: str, language: Optional[str] = None) -> dict:
        """Obtiene los conteos persistidos de una letra en un idioma, sin crear datos."""
        username_clean = (username or "").strip()
        letter_clean = (letter or "").strip().upper()
        if not username_clean or not letter_clean:
            return {"attempts": 0, "correct": 0, "incorrect": 0}

        field = self._language_field("learning_performance", language)
        users = self._users_collection()
        doc = users.find_one(
            {"username": username_clean},
            {f"{field}.{letter_clean}": 1},
        )
        stats = (doc or {}).get(field, {}).get(letter_clean, {})
        correct = int(stats.get("correct", 0))
        incorrect = int(stats.get("incorrect", 0))
        return {
            "attempts": min(int(stats.get("attempts", correct + incorrect)), MAX_ATTEMPTS),
            "correct": correct,
            "incorrect": incorrect,
        }

    def add_favorite_letter(self, username: str, letter: str, language: Optional[str] = None) -> list:
        """Guarda una letra favorita del idioma indicado en la cuenta del usuario."""
        return self._update_favorite_letters(username, letter, add=True, language=language)

    def remove_favorite_letter(self, username: str, letter: str, language: Optional[str] = None) -> list:
        """Elimina una letra favorita del idioma indicado de la cuenta del usuario."""
        return self._update_favorite_letters(username, letter, add=False, language=language)

    def get_favorite_letters(self, username: str, language: Optional[str] = None) -> list:
        """Obtiene las letras favoritas del idioma, ordenadas y sin duplicados."""
        username_clean = (username or "").strip()
        if not username_clean:
            return []
        field = self._language_field("favorite_letters", language)
        users = self._users_collection()
        doc = users.find_one({"username": username_clean}, {field: 1})
        return sorted(set((doc or {}).get(field, [])))

    def _update_favorite_letters(self, username: str, letter: str, add: bool, language: Optional[str] = None) -> list:
        username_clean = (username or "").strip()
        letter_clean = (letter or "").strip().upper()
        if not username_clean or not letter_clean:
            raise ValueError("El usuario y la letra son obligatorios")

        field = self._language_field("favorite_letters", language)
        users = self._users_collection()
        operation = {"$addToSet": {field: letter_clean}}
        if not add:
            operation = {"$pull": {field: letter_clean}}
        result = users.update_one({"username": username_clean}, operation)
        if result.matched_count != 1:
            raise ValueError("El usuario autenticado no existe")
        return self.get_favorite_letters(username_clean, language)
