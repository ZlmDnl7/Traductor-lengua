# text_to_speech.py
# Texto a voz de respaldo con las voces SAPI de Windows (System.Speech).
#
# La interfaz usa primero la Web Speech API de WebView2, pero WebView2 solo ve
# las voces "OneCore" de Windows; las voces de escritorio SAPI (p. ej.
# "Microsoft Zira Desktop", en-US) no le aparecen. Este modulo las usa a traves
# de PowerShell, sin dependencias de Python nuevas.
#
# Nunca se usa una voz de otro idioma: si no hay voz para el idioma (p. ej.
# pt-BR sin paquete de voz instalado) se informa "no_voice".

from __future__ import annotations

import re
import subprocess
import sys
import threading
from typing import List, Optional, Tuple

_LOCALE_RE = re.compile(r"^[a-z]{2}(-[A-Z]{2})?$")
_voices_cache: Optional[List[Tuple[str, str]]] = None
_process: Optional[subprocess.Popen] = None
_lock = threading.Lock()

_LIST_SCRIPT = (
    "Add-Type -AssemblyName System.Speech;"
    "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer;"
    "$s.GetInstalledVoices() | Where-Object { $_.Enabled } | "
    "ForEach-Object { $_.VoiceInfo.Culture.Name + '|' + $_.VoiceInfo.Name }"
)

# El texto llega por stdin (UTF-8) para no interpretarlo como codigo.
_SPEAK_SCRIPT = (
    "[Console]::InputEncoding = [System.Text.Encoding]::UTF8;"
    "Add-Type -AssemblyName System.Speech;"
    "$text = [Console]::In.ReadToEnd();"
    "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer;"
    "$s.SelectVoice('{voice}');"
    "$s.Speak($text)"
)


def _powershell(script: str, **kwargs) -> subprocess.Popen:
    flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    return subprocess.Popen(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
        creationflags=flags,
        **kwargs,
    )


def list_voices() -> List[Tuple[str, str]]:
    """[(cultura, nombre)] de las voces SAPI instaladas (vacio fuera de Windows)."""
    global _voices_cache
    if _voices_cache is not None:
        return _voices_cache
    voices: List[Tuple[str, str]] = []
    if sys.platform == "win32":
        try:
            proc = _powershell(_LIST_SCRIPT, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            out, _ = proc.communicate(timeout=20)
            for line in out.decode("utf-8", "replace").splitlines():
                culture, _, name = line.strip().partition("|")
                if culture and name:
                    voices.append((culture, name))
        except Exception:
            voices = []
    _voices_cache = voices
    return voices


def voice_for(locale: str, voices: Optional[List[Tuple[str, str]]] = None) -> Optional[str]:
    """Voz del mismo locale; si no existe, una del mismo idioma (es-ES para es-CO)."""
    voices = list_voices() if voices is None else voices
    wanted = (locale or "").lower()
    base = wanted.split("-")[0]
    for culture, name in voices:
        if culture.lower() == wanted:
            return name
    for culture, name in voices:
        if culture.lower().split("-")[0] == base:
            return name
    return None


def stop() -> None:
    global _process
    with _lock:
        if _process is not None and _process.poll() is None:
            _process.terminate()
        _process = None


def speak(text: str, locale: str) -> dict:
    """Lee el texto en segundo plano con una voz del idioma. Devuelve {ok, code, voice}."""
    global _process
    clean = (text or "").strip()
    if not clean:
        return {"ok": False, "code": "empty"}
    if not _LOCALE_RE.match(locale or ""):
        return {"ok": False, "code": "invalid_locale"}
    voice = voice_for(locale)
    if voice is None:
        return {"ok": False, "code": "no_voice"}
    stop()
    script = _SPEAK_SCRIPT.replace("{voice}", voice.replace("'", "''"))
    try:
        with _lock:
            _process = _powershell(script, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            _process.stdin.write(clean.encode("utf-8"))
            _process.stdin.close()
    except Exception:
        return {"ok": False, "code": "tts_error"}
    return {"ok": True, "code": "ok", "voice": voice}
