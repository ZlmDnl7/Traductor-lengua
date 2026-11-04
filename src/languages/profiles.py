# profiles.py
# Perfil centralizado de cada idioma de aprendizaje.
#
# Un perfil separa explicitamente:
#   - idioma de la interfaz (ui_locale) y en el que responde la IA,
#   - lengua de senas (LSC, ASL, LIBRAS) y su alfabeto,
#   - modelo de reconocimiento y datos de entrenamiento,
#   - recursos visuales (carpeta de imagenes),
#   - configuracion de voz (reconocimiento y texto a voz),
#   - palabras para los retos.
#
# Para agregar un idioma nuevo: crear su LanguageProfile aqui, sus textos en
# messages.py / sign_alphabets.py y sus textos de interfaz en web/i18n.js.

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple

from src.config import (
    DEFAULT_LEARNING_LANGUAGE,
    SIGN_ALPHABETS,
    SIGN_MODEL_FILES,
    WHISPER_HOTWORDS_FILE,
)


@dataclass(frozen=True)
class LanguageProfile:
    code: str                      # clave interna: es | en | pt
    ui_locale: str                 # idioma de interfaz y de respuesta de la IA
    speech_locale: str             # BCP-47 para voz a texto y texto a voz
    whisper_language: str          # codigo ISO-639-1 que entiende faster-whisper
    sign_language: str             # LSC | ASL | LIBRAS
    sign_language_name: str        # nombre de la lengua de senas, en su idioma
    display_name: str              # "Español — LSC"
    # Abecedario que se ensena (puede incluir letras que el modelo no detecta,
    # como la Ñ de LSC, que es una sena con movimiento).
    learning_alphabet: Tuple[str, ...]
    # Letras que el modelo puede producir (clases del modelo + letras de movimiento).
    model_alphabet: Tuple[str, ...]
    # Letras detectadas por movimiento (MotionDetector), no por el modelo ML.
    motion_letters: Tuple[str, ...]
    samples_csv: str
    model_path: str
    image_folder: str              # relativo a src/gui_web/web/
    hotwords_file: Optional[str]   # sesgo de vocabulario para Whisper (opcional)
    # Reto: como reducir caracteres que el alfabeto no tiene (p. ej. Ñ -> N en LSC
    # porque el modelo no detecta la Ñ). Las tildes siempre se eliminan.
    challenge_char_map: Dict[str, str] = field(default_factory=dict)
    # Reto: caracteres propios que se conservan (no se descomponen), p. ej. Ç.
    challenge_keep_chars: Tuple[str, ...] = ()
    challenge_words: Tuple[str, ...] = ()

    def as_dict(self) -> dict:
        return {
            "code": self.code,
            "ui_locale": self.ui_locale,
            "speech_locale": self.speech_locale,
            "whisper_language": self.whisper_language,
            "sign_language": self.sign_language,
            "sign_language_name": self.sign_language_name,
            "display_name": self.display_name,
            "learning_alphabet": list(self.learning_alphabet),
            "model_alphabet": list(self.model_alphabet),
            "motion_letters": list(self.motion_letters),
            "image_folder": self.image_folder,
            "challenge_words": list(self.challenge_words),
        }


_ES_CSV, _ES_MODEL = SIGN_MODEL_FILES["es"]
_EN_CSV, _EN_MODEL = SIGN_MODEL_FILES["en"]
_PT_CSV, _PT_MODEL = SIGN_MODEL_FILES["pt"]

LANGUAGE_PROFILES: Dict[str, LanguageProfile] = {
    "es": LanguageProfile(
        code="es",
        ui_locale="es-CO",
        speech_locale="es-CO",
        whisper_language="es",
        sign_language="LSC",
        sign_language_name="Lengua de Señas Colombiana",
        display_name="Español — LSC",
        learning_alphabet=tuple("ABCDEFGHIJKLMN") + ("Ñ",) + tuple("OPQRSTUVWXYZ"),
        model_alphabet=SIGN_ALPHABETS["es"],
        motion_letters=(),
        samples_csv=_ES_CSV,
        model_path=_ES_MODEL,
        image_folder="./assets/letras",
        hotwords_file=WHISPER_HOTWORDS_FILE,
        challenge_char_map={"Ñ": "N"},
        challenge_words=("HOLA", "AMIGO", "CASA", "GRACIAS", "FAMILIA", "AGUA", "SOL", "LUNA", "PAZ", "MANO"),
    ),
    "en": LanguageProfile(
        code="en",
        ui_locale="en-US",
        speech_locale="en-US",
        whisper_language="en",
        sign_language="ASL",
        sign_language_name="American Sign Language",
        display_name="English — ASL",
        learning_alphabet=SIGN_ALPHABETS["en"],
        model_alphabet=SIGN_ALPHABETS["en"],
        motion_letters=(),
        samples_csv=_EN_CSV,
        model_path=_EN_MODEL,
        image_folder="./assets/letras/asl",
        hotwords_file=None,
        challenge_char_map={"Ñ": "N", "Ç": "C"},
        challenge_words=("HELLO", "FRIEND", "LOVE", "HOUSE", "THANKS", "FAMILY", "WATER", "SUN", "HAND", "SIGN"),
    ),
    "pt": LanguageProfile(
        code="pt",
        ui_locale="pt-BR",
        speech_locale="pt-BR",
        whisper_language="pt",
        sign_language="LIBRAS",
        sign_language_name="Língua Brasileira de Sinais",
        display_name="Português — Libras",
        learning_alphabet=SIGN_ALPHABETS["pt"],
        model_alphabet=SIGN_ALPHABETS["pt"],
        motion_letters=("Ç",),
        samples_csv=_PT_CSV,
        model_path=_PT_MODEL,
        image_folder="./assets/letras/libras",
        hotwords_file=None,
        challenge_char_map={"Ñ": "N"},
        challenge_keep_chars=("Ç",),
        challenge_words=("OLÁ", "AMIGO", "CASA", "OBRIGADO", "FAMÍLIA", "ÁGUA", "SOL", "MÃO", "PAZ", "CORAÇÃO"),
    ),
}


def get_profile(language: Optional[str]) -> LanguageProfile:
    """Devuelve el perfil del idioma; si no existe usa el idioma por defecto."""
    return LANGUAGE_PROFILES.get(language or "", LANGUAGE_PROFILES[DEFAULT_LEARNING_LANGUAGE])


def normalize_language(language: Optional[str]) -> str:
    return get_profile(language).code


def project_path(relative: Optional[str]) -> Optional[str]:
    if not relative:
        return None
    if os.path.isabs(relative):
        return relative
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(root, relative)
