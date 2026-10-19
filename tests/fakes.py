# fakes.py
# Dobles de prueba compartidos: base de datos en memoria, autenticacion y un
# MainController sin camara (solo carga el clasificador del idioma activo).

from types import SimpleNamespace
from unittest import mock


class FakeDB:
    def __init__(self):
        self.users = {}
        self.attempts = {}
        self.favorites = {}

    def init_database(self):
        pass

    def _user(self, username):
        return self.users.setdefault(username, {"learning_language": "es"})

    def get_study_streak(self, username):
        return {"current_streak": 0, "best_streak": 0, "last_study_date": None}

    def get_color_blind_mode(self, u):
        return False

    def get_accessible_reading_mode(self, u):
        return False

    def get_dyslexia_spacing_mode(self, u):
        return False

    def get_reading_font_size(self, u):
        return "medium"

    def get_night_mode(self, u):
        return False

    def get_learning_language(self, u):
        return self._user(u)["learning_language"]

    def set_learning_language(self, u, lang):
        if lang not in ("es", "en", "pt"):
            raise ValueError("bad")
        self._user(u)["learning_language"] = lang
        return lang

    def record_learning_attempt(self, u, letter, ok, language=None):
        s = self.attempts.setdefault((language, letter), {"attempts": 0, "correct": 0, "incorrect": 0})
        s["attempts"] += 1
        s["correct" if ok else "incorrect"] += 1
        return dict(s)

    def get_learning_performance(self, u, letter, language=None):
        return dict(self.attempts.get((language, letter), {"attempts": 0, "correct": 0, "incorrect": 0}))

    def get_favorite_letters(self, u, language=None):
        return sorted(self.favorites.get(language, set()))

    def add_favorite_letter(self, u, letter, language=None):
        self.favorites.setdefault(language, set()).add(letter)
        return self.get_favorite_letters(u, language)

    def remove_favorite_letter(self, u, letter, language=None):
        self.favorites.setdefault(language, set()).discard(letter)
        return self.get_favorite_letters(u, language)


class FakeAuth:
    PASSWORD = "secret"

    def __init__(self, db):
        pass

    def login(self, username, password):
        if not username or password != self.PASSWORD:
            return None
        return SimpleNamespace(username=username)


def controller_patches(db):
    """Parches para crear un MainController sin MongoDB ni camara."""
    from src import main as main_module
    from src.sign_language.sign_classifier import SignClassifier

    return [
        mock.patch.object(main_module, "DatabaseManager", lambda: db),
        mock.patch.object(main_module, "AuthService", FakeAuth),
        mock.patch.object(
            main_module.MainController,
            "_start_translation_loop",
            lambda c: setattr(c, "_sign_classifier", SignClassifier(language=c._web_learning_language)),
        ),
    ]
