# Configuracion multilingue centralizada (idioma, lengua de senas, voz, IA).

from .ai_context import (
    AI_MODULES,
    MODULE_CHALLENGE,
    MODULE_EVALUATION,
    MODULE_INTERACTION,
    MODULE_LEARNING,
    MODULE_REVIEW,
    AIContext,
    build_ai_context,
)
from .messages import MESSAGES, t
from .profiles import LANGUAGE_PROFILES, LanguageProfile, get_profile, normalize_language, project_path
from .sign_alphabets import SIGN_ALPHABET_RULES, SignAlphabet, get_sign_alphabet


def language_pack(language: str) -> dict:
    """Todo lo que la interfaz necesita del idioma activo (perfil + instrucciones de cada sena)."""
    profile = get_profile(language)
    rules = get_sign_alphabet(profile.code)
    data = profile.as_dict()
    data["sign_descriptions"] = {L: rules.describe(L) for L in profile.learning_alphabet if rules.describe(L)}
    return data


__all__ = [
    "AI_MODULES",
    "MODULE_CHALLENGE",
    "MODULE_EVALUATION",
    "MODULE_INTERACTION",
    "MODULE_LEARNING",
    "MODULE_REVIEW",
    "AIContext",
    "build_ai_context",
    "MESSAGES",
    "t",
    "LANGUAGE_PROFILES",
    "LanguageProfile",
    "get_profile",
    "normalize_language",
    "project_path",
    "SIGN_ALPHABET_RULES",
    "SignAlphabet",
    "get_sign_alphabet",
    "language_pack",
]
