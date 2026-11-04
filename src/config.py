# config.py
# Constantes y configuracion centralizada del proyecto.
# Responsabilidad unica: definir parametros reutilizables.

import os

# Base de datos (MongoDB local para usar con Compass)
# Recomendado: MongoDB corriendo en localhost y Compass para visualizar.
MONGO_URI = "mongodb://localhost:27017"
MONGO_DB_NAME = "traductor_senas"
MONGO_USERS_COLLECTION = "users"

# Validacion de credenciales
MIN_USERNAME_LENGTH = 3
MAX_USERNAME_LENGTH = 50
MIN_PASSWORD_LENGTH = 6
MAX_PASSWORD_LENGTH = 100

# Camara
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Reconocimiento de manos
MIN_DETECTION_CONFIDENCE = 0.7
MIN_TRACKING_CONFIDENCE = 0.5

# Señas -> Texto (control de "ruido" y velocidad de escritura)
# Cuanto más alto, menos letras aleatorias y menos rápido escribe (recomendado para demo).
SIGN_STABILITY_FRAMES = 4           # frames iguales para mostrar letra (antes 10 = muy lento)
SIGN_COOLDOWN_MS = 650             # tiempo mínimo entre letras confirmadas
SIGN_RESET_NO_LETTER_FRAMES = 6    # cuántos frames sin letra para permitir la siguiente letra
LANDMARK_SMOOTH_ALPHA = 0.65       # suavizado visual (solo dibujo en run.py)
LANDMARK_SMOOTH_FOR_CLASSIFY = False  # False = clasificar con landmarks crudos (igual que al entrenar)

# Clasificador ML de senas (Random Forest / MLP sobre features geometricas)
SIGN_SAMPLES_PER_LETTER = 60
SIGN_SAMPLE_INTERVAL = 0.25          # segundos entre cada muestra guardada (mas alto = mas lento)
SIGN_CONFIDENCE_THRESHOLD = 0.55       # umbral del modelo (0.85 suele bloquear todo en vivo)
SIGN_DISPLAY_CONFIDENCE_THRESHOLD = 0.45  # mostrar letra en pill aunque aun no este "estable"
SIGN_USE_ML_TIEBREAKERS = False        # reglas extra; desactivadas para no pisar al Random Forest
SIGN_CLASSIFIER_TYPE = "rf"        # "rf" o "mlp"
SIGN_SAMPLES_CSV = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "sign_language",
    "sign_samples.csv",
)
SIGN_MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "sign_language",
    "sign_classifier.joblib",
)

# UI web: velocidad de video (más = más fluido, pero más CPU)
WEB_VIDEO_TARGET_WIDTH = 800       # ancho máximo del frame enviado a la UI
WEB_VIDEO_JPEG_QUALITY = 55        # 40-70 recomendado
WEB_VIDEO_INTERVAL_MS = 45         # cada cuántos ms se envía un frame (45ms ≈ 22 FPS)

# Interfaz
APP_TITLE = "Enseñando"
WINDOW_MIN_WIDTH = 800
WINDOW_MIN_HEIGHT = 600
MAX_ATTEMPTS = 5

# Idiomas disponibles para aprender lenguaje de señas: español, inglés, portugués.
LEARNING_LANGUAGES = ("es", "en", "pt")
DEFAULT_LEARNING_LANGUAGE = "es"

# Alfabeto dactilologico y modelo ML por idioma de aprendizaje.
# es usa LSC (Lengua de Senas Colombiana, modelo original); pt usa LIBRAS (Lingua
# Brasileira de Sinais) y en usa ASL (American Sign Language), cada uno con su propio
# dataset y modelo (se entrenan con: python collect_sign_samples.py --lang pt|en).
# El dataset de ASL se arma reutilizando las letras equivalentes de LSC y LIBRAS:
# python build_asl_dataset.py
_SIGN_DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "sign_language",
)
SIGN_ALPHABETS = {
    "es": tuple("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
    "en": tuple("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
    "pt": tuple("ABCÇDEFGHIJKLMNOPQRSTUVWXYZ"),
}
SIGN_MODEL_FILES = {
    "es": (SIGN_SAMPLES_CSV, SIGN_MODEL_PATH),
    "en": (
        os.path.join(_SIGN_DATA_DIR, "asl", "sign_samples.csv"),
        os.path.join(_SIGN_DATA_DIR, "asl", "sign_classifier.joblib"),
    ),
    "pt": (
        os.path.join(_SIGN_DATA_DIR, "libras", "sign_samples.csv"),
        os.path.join(_SIGN_DATA_DIR, "libras", "sign_classifier.joblib"),
    ),
}

# UI
# True = interfaz web moderna (HTML/CSS) embebida con PyWebView
# False = interfaz Tkinter/ttkbootstrap
USE_WEB_UI = True
WEB_DEPLOYMENT = os.getenv("WEB_DEPLOYMENT", "").strip().lower() in {"1", "true", "yes"}

# Reconocimiento de voz (Whisper local)
# Modelos: tiny, base, small, medium, large-v3 (más grande = mejor calidad, más lento y más RAM)
# Para conversación en CPU (baja latencia): "base" o "tiny".
# "small/medium" dan más precisión, pero pueden tardar demasiado en CPU.
WHISPER_MODEL_NAME = "base"
WHISPER_DEVICE = "cpu"
WHISPER_COMPUTE_TYPE = "int8"
VOICE_SAMPLE_RATE = 16000

# Micrófono de entrada (sounddevice)
# Si no detecta nada, fija aquí el índice del dispositivo de entrada.
# Ejemplos (según tu lista): 1 (Intel mic), 20 (Realtek mic).
# Déjalo en None para usar el micrófono por defecto de Windows.
# Si quieres fijarlo, pon el índice (ej: 1) o una parte del nombre (ej: \"Realtek\" / \"Intel\").
VOICE_INPUT_DEVICE = None

# Parámetros para velocidad (menos = más rápido, a costa de algo de precisión)
WHISPER_BEAM_SIZE = 1
WHISPER_BEST_OF = 1

# Lista de palabras/nombres para sesgar la transcripcion (mejora nombres propios)
# Archivo sugerido: data/hotwords_es.txt (una palabra o frase corta por linea)
WHISPER_HOTWORDS_FILE = "data/hotwords_es.txt"
WHISPER_HOTWORDS_MAX = 450              # lineas leidas del archivo (puede ser largo)
WHISPER_HOTWORDS_FOR_TRANSCRIBE = 55    # cuantas se envian (prioridad primero; mas = error de contexto)
WHISPER_INITIAL_PROMPT_WORDS = 0        # 0 = no usar initial_prompt (evita duplicar y reventar tokens)
