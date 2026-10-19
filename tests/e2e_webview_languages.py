# e2e_webview_languages.py
# Prueba de punta a punta de la interfaz real (index.html + app.js + WebAPI) en
# el motor real de PyWebView (WebView2 en Windows), con una base de datos en
# memoria y SIN camara ni microfono (las detecciones y la transcripcion se
# simulan escribiendo en el estado del controlador).
#
# Recorre el escenario de cambio de idioma:
#   ES (LSC) -> Aprendizaje -> EN (ASL) -> Repaso -> voz -> Reto -> PT (Libras) -> Interaccion
#
#   python tests/e2e_webview_languages.py
#
# Abre una ventana oculta y termina sola. Codigo de salida 0 = todo OK.

import json
import os
import sys
import threading
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import webview  # noqa: E402

from src.languages import get_sign_alphabet  # noqa: E402
from tests.fakes import FakeAuth, FakeDB, controller_patches  # noqa: E402

RESULTS = []
# Textos esperados del avance automatico en cada idioma.
AUTO_TEXTS = {
    "es": {"sl": "LSC", "advancing": "¡Correcto! Pasando a la siguiente letra…", "correct": "✓ Correcto",
           "learning_done": "🎉 ¡Completaste el abecedario de LSC!", "review_done": "🎉 ¡Repasaste todas tus letras favoritas!",
           "ask": "Llevas 4 intentos incorrectos con la letra {l}. ¿Quieres guardarla para repasarla después?",
           "already": "Llevas 4 intentos incorrectos con la letra {l}. Ya está guardada en tus letras para repasar.",
           "passed": "Letras que pasaste sin completar: {l}",
           "saved": "✓ Guardada para repasar"},
    "en": {"sl": "ASL", "advancing": "Correct! Moving to the next letter…", "correct": "✓ Correct",
           "learning_done": "🎉 You completed the ASL alphabet!", "review_done": "🎉 You reviewed all your favorite letters!",
           "ask": "You have 4 incorrect attempts with the letter {l}. Would you like to save it to review later?",
           "already": "You have 4 incorrect attempts with the letter {l}. It is already saved in your letters to review.",
           "passed": "Letters you skipped: {l}",
           "saved": "✓ Saved to review"},
    "pt": {"sl": "Libras", "advancing": "Correto! Indo para a próxima letra…", "correct": "✓ Correto",
           "learning_done": "🎉 Você concluiu o alfabeto de Libras!", "review_done": "🎉 Você revisou todas as suas letras favoritas!",
           "ask": "Você tem 4 tentativas incorretas com a letra {l}. Quer salvá-la para revisar depois?",
           "already": "Você tem 4 tentativas incorretas com a letra {l}. Ela já está salva nas suas letras para revisar.",
           "passed": "Letras que você pulou: {l}",
           "saved": "✓ Salva para revisar"},
}
SPANISH_WORDS = ("Volver", "Aprendizaje", "Letra detectada", "Cámara", "Iniciar", "Repaso", "Configuración", "señas")
ENGLISH_WORDS = ("Back", "Learning", "Detected letter", "Camera", "Start", "Review", "Settings", "signs")


def check(name, condition, detail=""):
    RESULTS.append((name, bool(condition), detail))
    print(("PASS " if condition else "FAIL ") + name + (f"  [{detail}]" if detail and not condition else ""))


def run_steps(window, controller, db):
    def js(code):
        return window.evaluate_js(code)

    def wait(sec=0.9):
        time.sleep(sec)

    def text(sel):
        return js(f"(document.querySelector({json.dumps(sel)})||{{}}).textContent||''").strip()

    def click(sel):
        js(f"document.querySelector({json.dumps(sel)}).click()")
        wait()

    def visible_text():
        return js("""(() => { const v=[...document.querySelectorAll('main > section, main > div')]
            .filter(e=>!e.classList.contains('hidden')); return v.map(e=>e.innerText).join('\\n'); })()""")

    def switch_language(code):
        js(f"""(() => {{ const i=document.querySelector('input[name="menuLearningLanguage"][value="{code}"]');
            i.checked=true; i.dispatchEvent(new Event('change')); }})()""")
        wait(1.5)

    # Las ventanas ocultas limitan los temporizadores a ~1 por segundo: la
    # deteccion se sostiene varios segundos para que lleguen 3 lecturas iguales.
    def hold_letter(letter, seconds=4.5):
        controller._web_letter = letter
        wait(seconds)
        controller._web_letter = None

    def wait_for(cond_js, timeout=8.0):
        end = time.time() + timeout
        while time.time() < end:
            if js(cond_js):
                return True
            time.sleep(0.2)
        return False

    def auto_advance_checks(lang):
        """Aprendizaje, Repaso y Reto avanzan solos al confirmar la sena (modelo del idioma)."""
        T = AUTO_TEXTS[lang]
        tag = lang.upper()
        check(f"{tag} modelo del idioma activo", controller._sign_classifier.language == lang)

        # --- Aprendizaje ---
        click("#btnOpenAprendizaje")
        check(f"{tag} aprendizaje: empieza en A", text("#learningLetter") == "A", text("#learningLetter"))
        controller._web_letter = "A"
        ok = wait_for(f"learningStatusPill.textContent === {json.dumps(T['correct'])}")
        check(f"{tag} aprendizaje: confirmacion visual", ok and text("#learningCaption") == T["advancing"], text("#learningCaption"))
        check(f"{tag} aprendizaje: aun no avanza (pausa ~1 s)", text("#learningLetter") == "A")
        ok = wait_for("learningLetter.textContent === 'B'")
        check(f"{tag} aprendizaje: avanza solo a B", ok, text("#learningLetter"))
        wait(3.0)  # la misma sena sigue en camara: no cuenta como intento de B ni avanza otra vez
        pill = text("#learningStatusPill")
        check(f"{tag} aprendizaje: una deteccion = un avance",
              text("#learningLetter") == "B" and pill != T["correct"] and not pill.startswith("✗"),
              text("#learningLetter") + " / " + pill)
        check(f"{tag} aprendizaje: intento de A registrado una vez",
              db.attempts.get((lang, "A"), {}).get("attempts") == 1, db.attempts.get((lang, "A")))
        controller._web_letter = "C"  # sena incorrecta para B
        ok = wait_for("learningStatusPill.textContent.startsWith('✗')")
        wait(2.0)
        check(f"{tag} aprendizaje: incorrecta permanece en B", ok and text("#learningLetter") == "B", text("#learningStatusPill"))
        controller._web_letter = "B"  # reintento correcto
        ok = wait_for("learningLetter.textContent === 'C'")
        check(f"{tag} aprendizaje: reintento correcto avanza a C", ok, text("#learningLetter"))
        controller._web_letter = None
        wait(1.2)

        # --- 4 errores en la misma letra: la IA ofrece guardarla para Repaso ---
        for letter in controller.web_get_favorite_letters()["letters"]:
            controller.web_set_favorite_letter(letter, False)
        js("refreshFavoriteLetters()")
        wait(0.6)

        def make_errors(n):
            for _ in range(n):
                controller._web_letter = "D"  # sena incorrecta para C
                wait_for("learningStatusPill.textContent.startsWith('✗') || !learningErrorPrompt.classList.contains('hidden')")
                controller._web_letter = None  # retira la mano: el siguiente es un intento nuevo
                wait_for("!learningStatusPill.textContent.startsWith('✗') || !learningErrorPrompt.classList.contains('hidden')")

        make_errors(3)
        check(f"{tag} errores: 3 errores no abren la pregunta", js("learningErrorPrompt.classList.contains('hidden')"))
        make_errors(1)
        ok = wait_for("!learningErrorPrompt.classList.contains('hidden')")
        check(f"{tag} errores: al 4.o error la IA pregunta (traducido)", ok and text("#learningErrorPromptMessage") == T["ask"].format(l="C"),
              text("#learningErrorPromptMessage"))
        controller._web_letter = "C"  # con la pregunta abierta no se cuenta ni se avanza
        wait(3.5)
        check(f"{tag} errores: deteccion en pausa mientras pregunta", text("#learningLetter") == "C")
        controller._web_letter = None
        click("#learningErrorPromptSave")
        wait(0.6)
        check(f"{tag} errores: letra guardada para repasar", "C" in controller.web_get_favorite_letters()["letters"])
        check(f"{tag} errores: boton confirma guardado", text("#learningErrorPromptSave") == T["saved"], text("#learningErrorPromptSave"))
        click("#learningErrorPromptKeep")
        check(f"{tag} errores: seguir practicando la misma letra",
              js("learningErrorPrompt.classList.contains('hidden')") and text("#learningLetter") == "C")
        make_errors(4)
        ok = wait_for("!learningErrorPrompt.classList.contains('hidden')")
        check(f"{tag} errores: ya guardada", ok and text("#learningErrorPromptMessage") == T["already"].format(l="C"),
              text("#learningErrorPromptMessage"))
        expected_next = js("LETTERS[LETTERS.indexOf('C') + 1]")  # Libras: C -> Ç
        click("#learningErrorPromptNext")
        check(f"{tag} errores: pasar a la siguiente letra ({expected_next})",
              js("learningErrorPrompt.classList.contains('hidden')") and text("#learningLetter") == expected_next,
              text("#learningLetter"))
        # Ultima letra -> mensaje de finalizacion
        js("learningIndex = LETTERS.length - 2; moveLearning(1)")
        check(f"{tag} aprendizaje: ultima letra Z", text("#learningLetter") == "Z")
        controller._web_letter = "Z"
        ok = wait_for("!learningComplete.classList.contains('hidden')")
        check(f"{tag} aprendizaje: mensaje de finalizacion", ok and text("#learningCompleteTitle") == T["learning_done"],
              text("#learningCompleteTitle"))
        wait(1.5)
        check(f"{tag} aprendizaje: no vuelve a la A", text("#learningLetter") == "Z")
        controller._web_letter = None
        wait(1.2)
        # Letras que el modelo no reconoce: aviso y avance manual
        notice = {}
        for letter in js("LETTERS"):
            js(f"learningIndex = LETTERS.indexOf({json.dumps(letter)}) - 1; moveLearning(1)")
            if not js("learningNotice.classList.contains('hidden')"):
                notice[letter] = text("#learningNotice")
        print(f"     {tag} letras sin reconocimiento del modelo:", notice or "(ninguna)")
        expected_missing = {"es": ["Ñ"], "en": [], "pt": []}[lang]
        check(f"{tag} aprendizaje: aviso de letras no reconocidas", sorted(notice) == expected_missing, notice)
        for msg in notice.values():
            check(f"{tag} aprendizaje: aviso traducido y con {T['sl']}", T["sl"] in msg, msg)
        click("#btnBackAprendizaje")

        # --- Repaso: dos favoritas -> avanza y termina ---
        for letter in controller.web_get_favorite_letters()["letters"]:
            controller.web_set_favorite_letter(letter, False)
        for letter in ("A", "B"):
            controller.web_set_favorite_letter(letter, True)
        click("#btnOpenRepaso")
        wait(0.6)
        check(f"{tag} repaso: empieza en A", text("#repasoLetter") == "A", text("#repasoLetter"))
        controller._web_letter = "A"
        ok = wait_for(f"repasoCaption.textContent === {json.dumps(T['advancing'])}")
        check(f"{tag} repaso: confirmacion visual", ok, text("#repasoCaption"))
        ok = wait_for("repasoLetter.textContent === 'B'")
        check(f"{tag} repaso: avanza solo a B", ok, text("#repasoLetter"))
        wait(2.5)
        check(f"{tag} repaso: sin intento extra por la misma sena",
              text("#repasoLetter") == "B" and len(controller._review_attempts) == 0,
              (text("#repasoLetter"), len(controller._review_attempts)))
        controller._web_letter = "B"
        ok = wait_for("!repasoComplete.classList.contains('hidden')")
        check(f"{tag} repaso: mensaje de finalizacion", ok and T["review_done"] in text("#repasoComplete"), text("#repasoComplete"))
        controller._web_letter = None
        wait(1.0)

        # --- Repaso: 4 errores -> la IA pregunta (la letra ya esta guardada) ---
        click("#btnRepasoRestart")
        check(f"{tag} repaso errores: ronda nueva en A", text("#repasoLetter") == "A", text("#repasoLetter"))

        def repaso_errors(n):
            for _ in range(n):
                start = js("repasoErrorCount")
                controller._web_letter = "D"
                wait_for(f"repasoErrorCount > {start} || repasoPrompt.open")
                controller._web_letter = None
                wait(0.8)

        repaso_errors(3)
        check(f"{tag} repaso errores: 3 errores no preguntan", not js("repasoPrompt.open"))
        repaso_errors(1)
        ok = wait_for("!repasoErrorPrompt.classList.contains('hidden')")
        check(f"{tag} repaso errores: la IA pregunta (ya guardada, traducido)",
              ok and text("#repasoErrorPromptMessage") == T["already"].format(l="A"), text("#repasoErrorPromptMessage"))
        check(f"{tag} repaso errores: guardar no aplica (ya guardada)",
              js("repasoErrorPromptSave.disabled") and text("#repasoErrorPromptSave") == T["saved"], text("#repasoErrorPromptSave"))
        controller._web_letter = "A"
        wait(2.5)
        check(f"{tag} repaso errores: deteccion en pausa", text("#repasoLetter") == "A" and js("repasoPrompt.open"))
        controller._web_letter = None
        click("#repasoErrorPromptKeep")
        check(f"{tag} repaso errores: seguir con la misma letra", not js("repasoPrompt.open") and text("#repasoLetter") == "A")
        repaso_errors(4)
        ok = wait_for("repasoPrompt.open")
        click("#repasoErrorPromptNext")
        check(f"{tag} repaso errores: pasar a la siguiente (B)", ok and not js("repasoPrompt.open") and text("#repasoLetter") == "B",
              text("#repasoLetter"))
        controller._web_letter = "B"
        ok = wait_for("!repasoComplete.classList.contains('hidden')")
        check(f"{tag} repaso errores: la ronda termina con la letra pasada", ok)
        controller._web_letter = None
        click("#btnBackRepaso")
        for letter in ("A", "B"):
            controller.web_set_favorite_letter(letter, False)

        # --- Reto: nombre "ana" ---
        # La ventana oculta lee el estado ~1 vez por segundo: se alarga la pausa
        # para poder ver la confirmacion (la duracion real de 1 s se prueba en
        # tests/test_multilingual.py con un reloj simulado).
        controller._challenge_advance_delay_s = 3.0
        click("#btnOpenReto")
        check(f"{tag} reto: letras ANA", controller._challenge_letters == list("ANA"), controller._challenge_letters)
        for letter, nxt in (("A", "N"), ("N", "A")):
            for _ in range(controller._challenge_hold_frames):
                controller._advance_challenge(letter)
            ok = wait_for(f"retoOverlay.textContent === {json.dumps(T['correct'])}", 3)
            check(f"{tag} reto: confirmacion de {letter}", ok and text("#retoCaption") == T["advancing"], text("#retoCaption"))
            controller._advance_challenge(None)
            ok = wait_for(f"retoLetter.textContent === {json.dumps(nxt)} && retoOverlay.textContent === ''")
            check(f"{tag} reto: avanza solo a {nxt}", ok, text("#retoLetter"))
        for _ in range(controller._challenge_hold_frames):
            controller._advance_challenge("A")
        ok = wait_for("!retoComplete.classList.contains('hidden')")
        check(f"{tag} reto: mensaje de finalizacion", ok and text("#retoCompleteText") != "", text("#retoComplete"))
        check(f"{tag} reto: sin letras pasadas", js("retoCompletePassed.classList.contains('hidden')"))

        # --- Reto: 4 errores -> pausa y pregunta de la IA ---
        for letter in controller.web_get_favorite_letters()["letters"]:
            controller.web_set_favorite_letter(letter, False)
        js("refreshFavoriteLetters()")
        click("#btnRetoRetry")

        def reto_errors(n, letter="B"):
            for _ in range(n):
                for _ in range(controller._challenge_hold_frames):
                    controller._advance_challenge(letter)
                controller._advance_challenge(None)

        reto_errors(3)
        wait(0.8)
        check(f"{tag} reto errores: 3 errores no preguntan", js("retoErrorPrompt.classList.contains('hidden')"))
        reto_errors(1)
        ok = wait_for("!retoErrorPrompt.classList.contains('hidden')")
        check(f"{tag} reto errores: la IA pregunta (traducido)",
              ok and text("#retoErrorPromptMessage") == T["ask"].format(l="A"), text("#retoErrorPromptMessage"))
        click("#retoErrorPromptSave")
        wait(0.6)
        check(f"{tag} reto errores: letra guardada para repasar", "A" in controller.web_get_favorite_letters()["letters"])
        check(f"{tag} reto errores: boton confirma guardado", text("#retoErrorPromptSave") == T["saved"], text("#retoErrorPromptSave"))
        click("#retoErrorPromptKeep")
        ok = wait_for("retoErrorPrompt.classList.contains('hidden')", 3)
        check(f"{tag} reto errores: seguir con la misma letra", ok and text("#retoLetter") == "A" and not controller._challenge_error_prompt)
        reto_errors(4)
        ok = wait_for("!retoErrorPrompt.classList.contains('hidden')")
        check(f"{tag} reto errores: ya guardada", ok and text("#retoErrorPromptMessage") == T["already"].format(l="A"),
              text("#retoErrorPromptMessage"))
        click("#retoErrorPromptNext")
        ok = wait_for("retoLetter.textContent === 'N' && retoErrorPrompt.classList.contains('hidden')", 3)
        check(f"{tag} reto errores: pasar a la siguiente (N)", ok, text("#retoLetter"))
        check(f"{tag} reto errores: letra pasada marcada",
              js("document.querySelector('#retoWord .reto-letter-tile').classList.contains('passed')"))
        for letter in ("N", "A"):
            for _ in range(controller._challenge_hold_frames):
                controller._advance_challenge(letter)
            wait_for("!document.querySelector('#retoWord .reto-letter-tile.current') || retoOverlay.textContent !== ''", 3)
            controller._advance_challenge(None)
            wait(controller._challenge_advance_delay_s + 0.6)
        ok = wait_for("!retoComplete.classList.contains('hidden')")
        check(f"{tag} reto errores: final con letras pasadas",
              ok and text("#retoCompletePassed") == T["passed"].format(l="A"), text("#retoCompletePassed"))
        click("#btnRetoMenu")
        controller._challenge_advance_delay_s = 1.0

    try:
        # Interfaz lista
        for _ in range(40):
            if js("typeof tr === 'function' && !!window.pywebview && !!window.pywebview.api"):
                break
            time.sleep(0.25)
        js("localStorage.clear()")

        # ===== Login en espanol =====
        check("login: titulo en espanol", text("#viewLogin h2") == "Iniciar sesión", text("#viewLogin h2"))
        js("document.getElementById('loginUser').value='ana'; document.getElementById('loginPass').value='bad'")
        click("#btnLogin")
        check("login: error en espanol", text("#loginError") == "Usuario o contraseña incorrectos", text("#loginError"))
        js(f"document.getElementById('loginPass').value='{FakeAuth.PASSWORD}'")
        click("#btnLogin")
        wait(1.0)
        check("menu visible tras login", not js("document.getElementById('viewMenu').classList.contains('hidden')"))

        # ===== 1) Espanol - LSC =====
        check("ES menu: Start Interaction en espanol", text("#btnOpenInteraction strong") == "Iniciar interacción")
        check("ES caption LSC", "LSC" in text("#menuLanguageCaption"), text("#menuLanguageCaption"))
        check("ES html lang", js("document.documentElement.lang") == "es-CO", js("document.documentElement.lang"))

        # ===== 2) Aprendizaje (LSC) =====
        click("#btnOpenAprendizaje")
        check("ES aprendizaje: imagen LSC", js("learningReferenceImage.getAttribute('src')") == "./assets/letras/a.png",
              js("learningReferenceImage.getAttribute('src')"))
        check("ES aprendizaje: instrucciones LSC", text("#learningInstructions") == get_sign_alphabet("es").describe("A"),
              text("#learningInstructions"))
        check("ES aprendizaje: abecedario LSC con Ñ", js("LETTERS.includes('Ñ') && LETTERS.length === 27"))
        controller._web_letter = "A"
        check("ES aprendizaje: correcto en espanol", wait_for("learningStatusPill.textContent === '✓ Correcto'"),
              text("#learningStatusPill"))
        wait_for("learningLetter.textContent === 'B'")
        controller._web_letter = None
        click("#btnPrevAprendizaje")  # el asistente muestra el analisis de la A
        js("document.getElementById('learningAssistantCard').classList.remove('hidden')")
        wait(0.6)
        check("ES asistente IA en espanol", "Continúa practicando" in text("#learningAssistantMessage"),
              text("#learningAssistantMessage"))
        click("#btnBackAprendizaje")

        # ===== 3) Cambiar a Ingles - ASL =====
        switch_language("en")
        check("EN menu: Start Interaction en ingles", text("#btnOpenInteraction strong") == "Start interaction")
        check("EN caption ASL", "ASL" in text("#menuLanguageCaption"))
        check("EN html lang", js("document.documentElement.lang") == "en-US", js("document.documentElement.lang"))
        check("EN backend actualizado", controller._web_learning_language == "en" and controller._review_ai.language == "en")
        check("EN modelo ASL cargado", controller._sign_classifier is not None and controller._sign_classifier.language == "en")
        check("EN imagenes del menu en ASL", js("[...document.querySelectorAll('.menu-word-tile img')].every(i=>i.getAttribute('src').startsWith('./assets/letras/asl/'))"))
        vt = visible_text()
        check("EN menu sin textos en espanol", not any(w in vt for w in SPANISH_WORDS), [w for w in SPANISH_WORDS if w in vt])

        # ===== 4) Repaso (ASL) =====
        click("#btnOpenRepaso")
        check("EN repaso vacio en ingles", text("#repasoEmptyState h2") == "You don't have favorite letters yet",
              text("#repasoEmptyState h2"))
        controller.web_set_favorite_letter("V", True)
        click("#btnBackRepaso")
        click("#btnOpenRepaso")
        wait(0.6)
        check("EN repaso: letra V", text("#repasoLetter") == "V", text("#repasoLetter"))
        check("EN repaso: imagen ASL", js("repasoReferenceImage.getAttribute('src')") == "./assets/letras/asl/v.png",
              js("repasoReferenceImage.getAttribute('src')"))
        check("EN repaso: instrucciones ASL", text("#repasoInstructions") == get_sign_alphabet("en").describe("V"))
        hold_letter("V")
        wait(0.6)
        check("EN repaso: IA responde en ingles (ASL)", "Great job" in text("#repasoAssistantMessage") and "ASL" in text("#repasoAssistantMessage"),
              text("#repasoAssistantMessage"))
        vt = visible_text()
        check("EN repaso sin textos en espanol", not any(w in vt for w in SPANISH_WORDS), [w for w in SPANISH_WORDS if w in vt])
        click("#btnBackRepaso")

        # ===== 5) Voz en ingles (transcripcion simulada: sin microfono) =====
        click("#btnOpenInteraction")
        check("EN interaccion: idioma de voz en-US", "en-US" in text("#voiceLanguage"), text("#voiceLanguage"))
        check("EN interaccion: boton Grabar", text("#btnRec") == "Record", text("#btnRec"))
        controller._voice_language = "en"
        controller._web_messages.append({"who": "Me (voice)", "kind": "voice", "text": "Hello there",
                                         "language": "en", "speech_locale": "en-US"})
        wait()
        check("EN chat: etiqueta en ingles", text("#chat .bubble .who") == "Me (voice)", text("#chat .bubble .who"))
        voices = js("speechSynthesis.getVoices().map(v => v.lang + ' | ' + v.name)")
        print("     voces disponibles en WebView2:", voices)
        js("speakText('Hola, esto es una prueba.', 'es-CO')")
        wait(1.0)
        check("ES texto a voz (voz de WebView2)", text("#ttsError") == "", text("#ttsError"))
        js("speakText('Hello, this is a test.', 'en-US')")
        wait(1.5)
        en_tts = text("#ttsError")
        check("EN texto a voz (voz en-US del equipo)", en_tts == "", en_tts)
        js("TTS.cancel()")
        vt = visible_text()
        check("EN interaccion sin textos en espanol", not any(w in vt for w in SPANISH_WORDS), [w for w in SPANISH_WORDS if w in vt])
        click("#btnBackInteraction")

        # ===== 6) Reto en ingles =====
        click("#btnOpenReto")
        check("EN reto: titulo", text("#retoTitle") == "Challenge: spell your name", text("#retoTitle"))
        check("EN reto: letras del nombre", js("[...document.querySelectorAll('#retoWord .reto-letter-tile')].map(t=>t.textContent).join('')") == "ANA")
        check("EN reto: instrucciones ASL", text("#retoInstructions") == get_sign_alphabet("en").describe("A"))
        for _ in range(controller._challenge_feedback_frames):
            controller._advance_challenge("B")
        wait()
        check("EN reto: pista de IA en ingles", not js("retoAiHint.classList.contains('hidden')") and text("#retoAiHintTitle") != "",
              text("#retoAiHintMessage"))
        click("#btnRetoWord")
        from src.languages import get_profile
        word = controller._challenge_word
        check("EN reto: palabra en ingles", word in get_profile("en").challenge_words and word in text("#retoTitle"), text("#retoTitle"))
        vt = visible_text()
        check("EN reto sin textos en espanol", not any(w in vt for w in SPANISH_WORDS), [w for w in SPANISH_WORDS if w in vt])
        click("#btnRetoBack")

        # ===== 7) Cambiar a Portugues - Libras =====
        switch_language("pt")
        check("PT menu: Start Interaction en portugues", text("#btnOpenInteraction strong") == "Iniciar interação")
        check("PT html lang", js("document.documentElement.lang") == "pt-BR")
        check("PT backend + modelo Libras", controller._web_learning_language == "pt" and controller._sign_classifier.language == "pt")
        check("PT reto reconstruido en portugues", controller._challenge_word in get_profile("pt").challenge_words or controller._challenge_mode == "name")
        vt = visible_text()
        check("PT menu sin textos en ingles", not any(w in vt for w in ENGLISH_WORDS), [w for w in ENGLISH_WORDS if w in vt])
        click("#btnOpenRepaso")
        check("PT repaso: favoritos propios de Libras (vacio)", text("#repasoEmptyState h2") == "Você ainda não tem letras favoritas",
              text("#repasoEmptyState h2"))
        click("#btnBackRepaso")
        click("#btnOpenAprendizaje")
        check("PT aprendizaje: abecedario con Ç", js("LETTERS.includes('Ç') && !LETTERS.includes('Ñ')"))
        check("PT aprendizaje: instrucciones Libras", text("#learningInstructions") == get_sign_alphabet("pt").describe("A"))
        check("PT aprendizaje: imagen Libras", js("learningReferenceImage.getAttribute('src')") == "./assets/letras/libras/a.png")
        click("#btnBackAprendizaje")
        click("#btnOpenReto")
        check("PT reto: titulo en portugues", text("#retoTitle") == "Desafio: soletre seu nome", text("#retoTitle"))
        click("#btnRetoBack")

        # ===== 8) Volver a Start Interaction =====
        click("#btnOpenInteraction")
        check("PT interaccion: idioma de voz pt-BR", "pt-BR" in text("#voiceLanguage"), text("#voiceLanguage"))
        check("PT chat: etiqueta re-traducida", text("#chat .bubble .who") == "Eu (voz)", text("#chat .bubble .who"))
        js("speakText('Olá, isto é um teste.', 'pt-BR')")
        wait(1.5)
        pt_tts = text("#ttsError")
        print("     resultado texto a voz pt-BR:", pt_tts or "(voz encontrada)")
        check("PT texto a voz: mensaje en portugues si falta la voz (nunca otra voz)",
              pt_tts == "" or pt_tts.startswith("Não há uma voz instalada para pt-BR"), pt_tts)
        js("TTS.cancel()")
        vt = visible_text()
        check("PT interaccion sin textos en ingles/espanol", not any(w in vt for w in ENGLISH_WORDS + ("Volver", "Grabar", "Cámara")),
              [w for w in ENGLISH_WORDS + ("Volver", "Grabar", "Cámara") if w in vt])
        click("#btnBackInteraction")

        # ===== 9) Avance automatico en los tres idiomas =====
        db.attempts.clear()
        for lang in ("es", "en", "pt"):
            switch_language(lang)
            auto_advance_checks(lang)

        # Cerrar sesion: el login conserva el ultimo idioma
        click("#btnLogoutMenu")
        check("logout: login en portugues", text("#viewLogin h2") == "Entrar", text("#viewLogin h2"))
        js("localStorage.clear()")
    except Exception as exc:  # pragma: no cover - reporte de la prueba
        import traceback

        traceback.print_exc()
        check("ejecucion sin excepciones", False, repr(exc))
    finally:
        window.destroy()


def main():
    # La ventana es oculta: sin esto WebView2 limita los temporizadores de la
    # pagina (a ~1 por minuto tras 5 minutos oculta) y el poll deja de leer el estado.
    os.environ.setdefault(
        "WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS",
        "--disable-background-timer-throttling --disable-renderer-backgrounding"
        " --disable-features=IntensiveWakeUpThrottling",
    )
    db = FakeDB()
    patches = controller_patches(db)
    for p in patches:
        p.start()
    try:
        from src.main import MainController

        controller = MainController()
        api = controller.get_web_api()
        html = os.path.join(ROOT, "src", "gui_web", "web", "index.html")
        window = webview.create_window("e2e", url=html, js_api=api, width=1280, height=800, hidden=True)
        webview.start(run_steps, (window, controller, db))
    finally:
        for p in patches:
            p.stop()
    failed = [r for r in RESULTS if not r[1]]
    print(f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} verificaciones OK")
    sys.exit(1 if failed or not RESULTS else 0)


if __name__ == "__main__":
    main()
