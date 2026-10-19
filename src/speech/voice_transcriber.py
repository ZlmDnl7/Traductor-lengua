# voice_transcriber.py
# Grabacion con microfono y transcripcion con faster-whisper (local, open source).
# El idioma de transcripcion sale del perfil del idioma de aprendizaje
# (src/languages/profiles.py): es-CO -> "es", en-US -> "en", pt-BR -> "pt".
# El modelo de Whisper configurado (WHISPER_MODEL_NAME) debe ser multilingue
# (tiny/base/small/medium/large-v3, NO las variantes ".en").

import threading
from typing import Optional

import numpy as np

from src.config import VOICE_SAMPLE_RATE

_model = None
_hotwords_data_cache: dict = {}


class VoiceInputError(RuntimeError):
    """Error de microfono con un codigo traducible (ver src/languages/messages.py)."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def _load_hotwords_data(language: str = "es") -> dict:
    """Devuelve {'priority': [...], 'all': [...]} desde el archivo de hotwords del idioma."""
    if language in _hotwords_data_cache:
        return _hotwords_data_cache[language]
    empty = {"priority": [], "all": []}
    try:
        import os
        from src.config import WHISPER_HOTWORDS_MAX
        from src.languages import get_profile, project_path

        path = project_path(get_profile(language).hotwords_file)
        if not path or not os.path.exists(path):
            _hotwords_data_cache[language] = empty
            return empty

        cap = int(WHISPER_HOTWORDS_MAX)
        priority: list = []
        all_items: list = []
        seen: set = set()
        in_priority = False

        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                raw = line.strip()
                if raw.startswith("#"):
                    upper = raw.upper()
                    if "PRIORIDAD WHISPER" in upper:
                        in_priority = True
                    elif raw.startswith("# ---") and in_priority:
                        in_priority = False
                    continue
                if not raw:
                    continue
                key = raw.lower()
                if key in seen:
                    continue
                seen.add(key)
                all_items.append(raw)
                if in_priority:
                    priority.append(raw)

        data = {"priority": priority, "all": all_items[:cap]}
        _hotwords_data_cache[language] = data
        return data
    except Exception:
        _hotwords_data_cache[language] = empty
        return empty


def load_hotwords(language: str = "es") -> list:
    """Lista completa de hotwords del idioma (vacia si el idioma no tiene archivo)."""
    return _load_hotwords_data(language)["all"]


def _whisper_bias_strings(hotwords: list, language: str = "es") -> tuple[Optional[str], Optional[str]]:
    """
    Arma sesgo corto para Whisper. El modelo base tiene limite ~448 tokens de prompt;
    pasar 400+ hotwords rompe con 'No position encodings are defined for positions >= 448'.
    """
    data = _load_hotwords_data(language)
    priority = data.get("priority") or []
    if not hotwords and not priority:
        return None, None
    try:
        from src.config import WHISPER_HOTWORDS_FOR_TRANSCRIBE, WHISPER_INITIAL_PROMPT_WORDS
        n_hw = max(0, int(WHISPER_HOTWORDS_FOR_TRANSCRIBE))
        n_pr = max(0, int(WHISPER_INITIAL_PROMPT_WORDS))
    except Exception:
        n_hw, n_pr = 55, 0

    hotwords_str = None
    if n_hw > 0:
        ordered: list = []
        seen: set = set()
        for w in priority:
            k = w.lower()
            if k not in seen:
                seen.add(k)
                ordered.append(w)
        for w in hotwords:
            k = w.lower()
            if k not in seen:
                seen.add(k)
                ordered.append(w)
            if len(ordered) >= n_hw:
                break
        hotwords_str = " ".join(ordered[:n_hw])
        if len(hotwords_str) > 500:
            hotwords_str = hotwords_str[:500].rsplit(" ", 1)[0]

    initial_prompt = None
    if n_pr > 0:
        chunk = (priority + hotwords)[:n_pr]
        initial_prompt = ", ".join(chunk) + "."
        if len(initial_prompt) > 350:
            initial_prompt = initial_prompt[:350].rsplit(",", 1)[0] + "."

    return hotwords_str, initial_prompt


def trim_audio_edges(audio: np.ndarray, samplerate: int = VOICE_SAMPLE_RATE) -> np.ndarray:
    """
    Recorta silencio muy bajo al inicio y final para reducir alucinaciones de Whisper
    cuando queda mucho audio vacio tras dejar de hablar.
    """
    if audio.size == 0:
        return audio
    peak = float(np.max(np.abs(audio)))
    if peak < 1e-6:
        return audio
    # Muy conservador: preferimos NO recortar para no perder sílabas.
    thr = max(0.0015, peak * 0.015)
    above = np.abs(audio) > thr
    if not np.any(above):
        return audio
    idx = np.flatnonzero(above)
    lo, hi = int(idx[0]), int(idx[-1]) + 1
    pad = int(0.12 * samplerate)
    lo = max(0, lo - pad)
    hi = min(len(audio), hi + pad)
    return audio[lo:hi]


def record_until_stop(stop_event: threading.Event, samplerate: int = VOICE_SAMPLE_RATE) -> np.ndarray:
    """
    Graba desde el microfono hasta que stop_event se active (mismo hilo que llama a esta funcion).
    """
    import sounddevice as sd

    chunks: list = []
    lock = threading.Lock()

    def callback(indata, frames, time, status) -> None:
        if status:
            pass
        with lock:
            chunks.append(indata.copy().flatten())

    from src.config import VOICE_INPUT_DEVICE

    def resolve_input_device():
        # Permite VOICE_INPUT_DEVICE como: None, int, o str (parte del nombre)
        if VOICE_INPUT_DEVICE is None or VOICE_INPUT_DEVICE == "":
            # Usar el dispositivo predeterminado de Windows (lo más confiable)
            return None
        try:
            if isinstance(VOICE_INPUT_DEVICE, int):
                sd.query_devices(VOICE_INPUT_DEVICE, "input")
                return VOICE_INPUT_DEVICE
            # string: buscar por nombre
            needle = str(VOICE_INPUT_DEVICE).lower().strip()
            for i, d in enumerate(sd.query_devices()):
                if d.get("max_input_channels", 0) > 0 and needle in str(d.get("name", "")).lower():
                    return i
        except Exception:
            return None
        return None

    device = resolve_input_device()

    def _hostapi_preference_rank(name: str) -> int:
        n = (name or "").lower()
        if "wasapi" in n:
            return 0
        if "directsound" in n:
            return 1
        if "wdm" in n or "ks" in n:
            return 2
        if "mme" in n:
            return 3
        return 4

    def _device_candidates() -> list:
        """
        Devuelve una lista corta de candidatos (dev_id o None) priorizando WASAPI/DirectSound.
        """
        candidates = []
        if device is not None:
            candidates.append(device)
        candidates.append(None)  # default del sistema (a veces es el único que funciona)

        try:
            hostapis = sd.query_hostapis()
            devs = sd.query_devices()

            # ordenar hostapis por preferencia
            hostapi_order = sorted(
                [(i, h) for i, h in enumerate(hostapis)],
                key=lambda x: _hostapi_preference_rank(str(x[1].get("name", ""))),
            )

            # default input de cada hostapi preferido
            for i, h in hostapi_order:
                dflt = h.get("default_input_device", None)
                if dflt is not None and int(dflt) >= 0:
                    candidates.append(int(dflt))

            # algunos inputs adicionales (limitado para no demorar)
            for i, h in hostapi_order:
                count = 0
                for idx, d in enumerate(devs):
                    if int(d.get("hostapi", -1)) != int(i):
                        continue
                    if d.get("max_input_channels", 0) <= 0:
                        continue
                    candidates.append(idx)
                    count += 1
                    if count >= 3:
                        break
        except Exception:
            pass

        # quitar duplicados manteniendo orden
        seen = set()
        out = []
        for c in candidates:
            if c in seen:
                continue
            seen.add(c)
            out.append(c)
        return out

    def _extra_settings_for_dev(dev_id):
        # Solo aplica WASAPI settings cuando el device pertenezca a WASAPI (evita errores raros)
        try:
            if dev_id is None:
                return None
            d = sd.query_devices(dev_id, "input")
            hostapi_name = sd.query_hostapis(int(d.get("hostapi", -1))).get("name", "")
            if "wasapi" in str(hostapi_name).lower():
                return sd.WasapiSettings(exclusive=False)
        except Exception:
            return None
        return None

    def _try_open_stream(dev_id):
        """
        Intenta abrir el stream con varios samplerates. Retorna (stream_ctx, native_rate, device_info)
        """
        device_info = sd.query_devices(dev_id, "input") if dev_id is not None else sd.query_devices(sd.default.device[0], "input")
        base_rate = int(device_info.get("default_samplerate", samplerate)) or samplerate
        extra = _extra_settings_for_dev(dev_id)

        def _open(rate):
            return sd.InputStream(
                samplerate=rate,
                channels=1,
                dtype="float32",
                callback=callback,
                device=dev_id,
                extra_settings=extra,
            )

        for r in (base_rate, 48000, 44100, 32000, 16000):
            try:
                return _open(int(r)), int(r), device_info
            except Exception:
                continue
        raise VoiceInputError("mic_open_failed", "No se pudo abrir el micrófono con ningún samplerate compatible.")

    # Probar candidatos hasta que uno abra de verdad (evita -9996/-9999)
    last_err = None
    stream_ctx = None
    device_info = None
    native_rate = samplerate
    chosen_dev = None
    for cand in _device_candidates():
        try:
            stream_ctx, native_rate, device_info = _try_open_stream(cand)
            chosen_dev = cand
            break
        except Exception as e:
            last_err = e
            continue
    if stream_ctx is None:
        raise VoiceInputError(
            "mic_open_failed",
            "No se pudo abrir el micrófono. "
            "Cierra apps que usen el micrófono (Chrome/Teams/Zoom) y prueba de nuevo. "
            "Si persiste, configura VOICE_INPUT_DEVICE en src/config.py (por ejemplo \"Intel\" o \"Realtek\")."
        ) from last_err

    try:
        with stream_ctx:
            while not stop_event.is_set():
                stop_event.wait(0.05)
    finally:
        # Asegurar liberación del dispositivo en Windows (evita que quede "ocupado")
        try:
            stream_ctx.close()
        except Exception:
            pass
        try:
            sd.stop()
        except Exception:
            pass

    with lock:
        if not chunks:
            return np.array([], dtype=np.float32)
        audio = np.concatenate(chunks).astype(np.float32)

        # Normalización suave para micros con poca ganancia (sin clip)
        peak = float(np.max(np.abs(audio))) if audio.size else 0.0
        if peak > 1e-6 and peak < 0.2:
            gain = min(6.0, 0.2 / peak)
            audio = np.clip(audio * gain, -1.0, 1.0).astype(np.float32)
            peak = float(np.max(np.abs(audio))) if audio.size else peak

        # Re-muestreo a 16k si el stream se abrió con otro rate
        if native_rate != samplerate and audio.size > 0:
            audio = resample_audio(audio, native_rate, samplerate)

        peak2 = float(np.max(np.abs(audio))) if audio.size else 0.0
        # Log corto para debug (sale en consola)
        try:
            dev_name = device_info.get("name", "default") if device_info else "default"
        except Exception:
            dev_name = "default"
        print(f"[voice] device={dev_name} dev_id={chosen_dev} native_rate={native_rate} -> {samplerate} peak={peak2:.4f}")

        # Si tras normalizar sigue siendo casi silencio, fallar con mensaje accionable
        if audio.size and peak2 < 0.002:
            raise VoiceInputError(
                "mic_silent",
                "No se detectó audio del micrófono (señal casi en cero). "
                "Ve a Windows > Sonido > Entrada y selecciona el micrófono correcto. "
                "Luego fija VOICE_INPUT_DEVICE en src/config.py con \"Intel\" o \"Realtek\"."
            )
        return audio

def resample_audio(audio: np.ndarray, src_rate: int, dst_rate: int) -> np.ndarray:
    """
    Re-muestreo sin dependencias extra.
    Preferimos `audioop.ratecv` (mejor calidad) y caemos a interpolación si no está disponible.
    """
    if src_rate == dst_rate or audio.size == 0:
        return audio.astype(np.float32, copy=False)
    try:
        import audioop

        # float32 [-1, 1] -> int16 PCM
        pcm = np.clip(audio, -1.0, 1.0)
        pcm16 = (pcm * 32767.0).astype(np.int16, copy=False).tobytes()
        converted, _state = audioop.ratecv(pcm16, 2, 1, int(src_rate), int(dst_rate), None)
        out = np.frombuffer(converted, dtype=np.int16).astype(np.float32) / 32767.0
        return out
    except Exception:
        # Fallback: interpolación lineal
        ratio = float(dst_rate) / float(src_rate)
        n_dst = max(1, int(round(audio.size * ratio)))
        x_old = np.linspace(0.0, 1.0, num=audio.size, endpoint=False, dtype=np.float64)
        x_new = np.linspace(0.0, 1.0, num=n_dst, endpoint=False, dtype=np.float64)
        out = np.interp(x_new, x_old, audio.astype(np.float64))
        return out.astype(np.float32)


def record_mono_float32(seconds: float, samplerate: int = VOICE_SAMPLE_RATE) -> np.ndarray:
    """Graba audio monofonico float32 [-1, 1] compatible con Whisper."""
    import sounddevice as sd

    if seconds <= 0:
        raise ValueError("La duracion de grabacion debe ser positiva")
    frames = int(seconds * samplerate)
    if frames < 1:
        frames = 1
    data = sd.rec(frames, samplerate=samplerate, channels=1, dtype="float32")
    sd.wait()
    return np.squeeze(data).astype(np.float32)


def transcribe_spanish(
    audio: np.ndarray,
    samplerate: int = VOICE_SAMPLE_RATE,
    model_name: Optional[str] = None,
) -> str:
    """Compatibilidad: transcribe en espanol."""
    return transcribe(audio, "es", samplerate=samplerate, model_name=model_name)


def transcribe(
    audio: np.ndarray,
    language: str = "es",
    samplerate: int = VOICE_SAMPLE_RATE,
    model_name: Optional[str] = None,
) -> str:
    """
    Transcribe audio a texto en el idioma de aprendizaje indicado (es | en | pt).
    Whisper recibe el idioma de forma explicita para que no traduzca ni mezcle
    idiomas. Descarga el modelo la primera vez.
    """
    global _model
    from src.languages import get_profile

    profile = get_profile(language)
    whisper_language = profile.whisper_language
    from faster_whisper import WhisperModel

    from src.config import (
        WHISPER_BEAM_SIZE,
        WHISPER_BEST_OF,
        WHISPER_COMPUTE_TYPE,
        WHISPER_DEVICE,
        WHISPER_MODEL_NAME,
    )

    name = model_name or WHISPER_MODEL_NAME
    if _model is None:
        _model = WhisperModel(name, device=WHISPER_DEVICE, compute_type=WHISPER_COMPUTE_TYPE)

    if audio.size == 0:
        return ""

    # Evitar recortes si ya estamos teniendo texto vacío frecuentemente
    audio = np.ascontiguousarray(audio, dtype=np.float32)
    if audio.size == 0:
        return ""

    hotwords = load_hotwords(profile.code)
    hotwords_str, initial_prompt = _whisper_bias_strings(hotwords, profile.code)

    base_kwargs = dict(
        language=whisper_language,
        beam_size=int(WHISPER_BEAM_SIZE),
        best_of=int(WHISPER_BEST_OF),
        vad_filter=False,
        condition_on_previous_text=False,
        compression_ratio_threshold=2.4,
        log_prob_threshold=-2.0,
        no_speech_threshold=0.15,
        initial_prompt=initial_prompt,
    )
    # En tu versión de faster-whisper, `hotwords` debe ser STR (si se pasa como list, adentro hace hotwords.strip()).
    # Por eso aquí SIEMPRE lo pasamos como string cuando exista.
    def _collect_text(segs) -> str:
        parts: list = []
        for s in segs:
            raw = getattr(s, "text", "")
            if isinstance(raw, list):
                t = " ".join(str(x) for x in raw).strip()
            else:
                t = str(raw).strip()
            if not t:
                continue
            if parts and t == parts[-1]:
                continue
            parts.append(t)
        return " ".join(parts).strip()

    def _transcribe_once(use_hotwords: bool):
        kw = dict(base_kwargs)
        if use_hotwords and hotwords_str:
            return _model.transcribe(audio, hotwords=hotwords_str, **kw)
        kw["initial_prompt"] = None
        return _model.transcribe(audio, **kw)

    text = ""
    try:
        segments, _info = _transcribe_once(use_hotwords=bool(hotwords_str))
        text = _collect_text(segments)
    except RuntimeError:
        # Prompt/hotwords demasiado largos u otro fallo del decoder -> voz normal sin sesgo.
        segments, _info = _transcribe_once(use_hotwords=False)
        text = _collect_text(segments)
    except Exception:
        segments, _info = _transcribe_once(use_hotwords=False)
        text = _collect_text(segments)
    if text:
        return _postprocess(text, profile.code)

    # Segundo intento (fallback ultra-permisivo). A veces faster-whisper decide "no speech"
    # por thresholds internos; este fallback fuerza a devolver algo si hay voz.
    fallback_kwargs = dict(
        language=whisper_language,
        beam_size=1,
        best_of=1,
        vad_filter=False,
        condition_on_previous_text=False,
        compression_ratio_threshold=10.0,
        log_prob_threshold=-10.0,
        no_speech_threshold=1.0,
    )
    try:
        segments2, _info2 = _model.transcribe(audio, **fallback_kwargs)
        return _postprocess(_collect_text(segments2), profile.code)
    except Exception:
        return ""


def _postprocess(text: str, language: str) -> str:
    """Correcciones propias de cada idioma (hoy solo existen para espanol)."""
    if language == "es":
        return _postprocess_spanish(text)
    return (text or "").strip()


def _postprocess_spanish(text: str) -> str:
    """
    Normalizaciones pequeñas para evitar resultados raros muy comunes en es-ES/LatAm.
    No intenta "corregir" todo, solo casos frecuentes.
    """
    import re

    t = (text or "").strip()
    if not t:
        return ""

    # Caso reportado: "AYER" -> "Ajérd"/"Ajér"/variantes
    t = re.sub(r"\baj[ée]r(d)?\b", "ayer", t, flags=re.IGNORECASE)

    # "Medellín" mal oido por Whisper base (Meijin, Medgin, Medín, Mede G...)
    t = re.sub(r"\bmeijin\b", "Medellín", t, flags=re.IGNORECASE)
    t = re.sub(r"\bmedgin\b", "Medellín", t, flags=re.IGNORECASE)
    t = re.sub(r"\bmedín\b", "Medellín", t, flags=re.IGNORECASE)
    t = re.sub(r"\bmede\s+g\b", "Medellín", t, flags=re.IGNORECASE)
    t = re.sub(r"\bmedellin\b", "Medellín", t, flags=re.IGNORECASE)

    t = re.sub(r"\bhello\b", "hola", t, flags=re.IGNORECASE)

    return t.strip()

