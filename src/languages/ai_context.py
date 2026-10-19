# ai_context.py
# Contexto centralizado que reciben los motores de IA del proyecto
# (ReviewAI en Repaso, LearningPerformanceAnalyzer en Aprendizaje y Reto).
#
# Reune en un solo objeto todo lo que la IA necesita para responder en el
# idioma correcto y evaluar con las reglas del alfabeto correcto:
#   1. idioma seleccionado          5. instrucciones correctas de la sena
#   2. lengua de senas              6. idioma de respuesta
#   3. alfabeto utilizado           7. modulo donde esta el usuario
#   4. letra evaluada

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

from .profiles import get_profile
from .sign_alphabets import SignAlphabet, get_sign_alphabet

MODULE_LEARNING = "learning"
MODULE_REVIEW = "review"
MODULE_CHALLENGE = "challenge"
MODULE_INTERACTION = "interaction"
MODULE_EVALUATION = "evaluation"
AI_MODULES = (MODULE_LEARNING, MODULE_REVIEW, MODULE_CHALLENGE, MODULE_INTERACTION, MODULE_EVALUATION)


@dataclass(frozen=True)
class AIContext:
    language: str
    sign_language: str
    sign_language_name: str
    alphabet: Tuple[str, ...]
    letter: Optional[str]
    instructions: Optional[str]
    response_language: str
    module: str

    @property
    def rules(self) -> SignAlphabet:
        return get_sign_alphabet(self.language)

    def for_letter(self, letter: Optional[str]) -> "AIContext":
        return build_ai_context(self.language, self.module, letter)

    def as_dict(self) -> dict:
        return {
            "language": self.language,
            "sign_language": self.sign_language,
            "sign_language_name": self.sign_language_name,
            "alphabet": list(self.alphabet),
            "letter": self.letter,
            "instructions": self.instructions,
            "response_language": self.response_language,
            "module": self.module,
        }


def build_ai_context(language: str, module: str = MODULE_REVIEW, letter: Optional[str] = None) -> AIContext:
    profile = get_profile(language)
    rules = get_sign_alphabet(profile.code)
    target = (letter or "").strip().upper() or None
    return AIContext(
        language=profile.code,
        sign_language=profile.sign_language,
        sign_language_name=profile.sign_language_name,
        alphabet=profile.learning_alphabet,
        letter=target,
        instructions=rules.describe(target) if target else None,
        response_language=profile.ui_locale,
        module=module if module in AI_MODULES else MODULE_REVIEW,
    )
