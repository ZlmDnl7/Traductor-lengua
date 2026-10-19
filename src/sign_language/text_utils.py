# text_utils.py
# Utilidades de texto para el modulo de senas (reto "deletrea tu nombre / una palabra").

from __future__ import annotations

import unicodedata
from typing import Iterable, List, Optional, Tuple

from src.languages import get_profile


def spell_text(
    text: str,
    language: str = "es",
    allowed: Optional[Iterable[str]] = None,
) -> Tuple[List[str], List[str]]:
    """
    Convierte un texto en la secuencia de letras deletreables con el alfabeto
    dactilologico del idioma y devuelve tambien los caracteres descartados.

    - Quita tildes (JOSÉ -> JOSE, OLÁ -> OLA).
    - Aplica las reducciones del perfil (LSC y ASL: Ñ -> N; ASL: Ç -> C).
    - Conserva las letras propias del alfabeto (LIBRAS: Ç).
    - Descarta espacios, numeros y simbolos.
    - Si se indica `allowed` (letras que el modelo puede reconocer), descarta
      las demas para que el reto nunca quede bloqueado en una letra imposible.

    Ejemplo: spell_text("María José", "es") -> (["M","A","R","I","A","J","O","S","E"], [" "])
    """
    if not text:
        return [], []
    profile = get_profile(language)
    allowed_set = {str(L).upper() for L in allowed} if allowed is not None else None
    letters: List[str] = []
    skipped: List[str] = []
    for ch in text.strip().upper():
        if ch in profile.challenge_keep_chars:
            candidates = [ch]
        else:
            ch_mapped = profile.challenge_char_map.get(ch, ch)
            candidates = [c for c in unicodedata.normalize("NFKD", ch_mapped) if "A" <= c <= "Z"]
        if not candidates:
            if not ch.isspace():
                skipped.append(ch)
            continue
        for c in candidates:
            if allowed_set is not None and c not in allowed_set:
                skipped.append(c)
                continue
            letters.append(c)
    return letters, skipped


def letters_for_challenge(text: str, language: str = "es", allowed: Optional[Iterable[str]] = None) -> List[str]:
    """
    Compatibilidad: solo la lista de letras deletreables.

    Ejemplo: "María José" -> ["M", "A", "R", "I", "A", "J", "O", "S", "E"]
    """
    return spell_text(text, language, allowed)[0]
