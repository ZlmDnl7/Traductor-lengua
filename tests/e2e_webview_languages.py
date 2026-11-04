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
SPANISH_WORDS = ("Volver", "Aprendizaje", "Letra detectada", "Cámara", "Iniciar", "Repaso", "Configuración", "señas")
ENGLISH_WORDS = ("Back", "Learning", "Detected letter", "Camera", "Start", "Review", "Settings", "signs")


def check(name, condition, detail=""):
    RESULTS.append((name, bool(condition), detail))
    print(("PASS " if condition else "FAIL ") + name + (f"  [{detail}]" if detail and not condition else ""))


def run_steps(window, controller):
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
        hold_letter("A")
        check("ES aprendizaje: correcto en espanol", text("#learningStatusPill") == "✓ Correcto", text("#learningStatusPill"))
        js("document.getElementById('learningAssistantCard').classList.remove('hidden')")
        wait(0.6)
        check("ES asistente IA en espanol", "Continúa practicando" in text("#learningAssistantMessage"),
              text("#learningAssistantMessage"))
        click("#btnBackAprendizaje")
        click("#btnOpenProfile")
        check("ES perfil: nombre y progreso guardado", text("#profileUsername") == "ana" and text("#profileProgressCount") == "1 de 27 letras",
              text("#profileUsername") + " / " + text("#profileProgressCount"))
        click("#btnBackProfile")

        # ===== 3) Cambiar a Ingles - ASL =====
        switch_language("en")
        check("EN menu: Start Interaction en ingles", text("#btnOpenInteraction strong") == "Start interaction")
        check("EN caption ASL", "ASL" in text("#menuLanguageCaption"))
        check("EN html lang", js("document.documentElement.lang") == "en-US", js("document.documentElement.lang"))
        check("EN backend actualizado", controller._web_learning_language == "en" and controller._review_ai.language == "en")
        check("EN modelo ASL cargado", controller._sign_classifier is not None and controller._sign_classifier.language == "en")
        check("EN imagenes del menu en ASL", js("[...document.querySelectorAll('.dash-word-tile img')].every(i=>i.getAttribute('src').startsWith('./assets/letras/asl/'))"))
        vt = visible_text()
        check("EN menu sin textos en espanol", not any(w in vt for w in SPANISH_WORDS), [w for w in SPANISH_WORDS if w in vt])
        click("#btnOpenProfile")
        check("EN perfil: traducción y alfabeto ASL", text("#viewProfile .view-title") == "My learning profile" and text("#profileProgressCount") == "0 of 26 letters",
              text("#viewProfile .view-title") + " / " + text("#profileProgressCount"))
        click("#btnBackProfile")

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

        # Cerrar sesion: vuelve a la portada y el login conserva el ultimo idioma
        click("#btnLogout")
        check("logout: vuelve a la portada", not js("document.getElementById('viewLanding').classList.contains('hidden')"))
        check("logout: login en portugues", text("#viewLogin h2") == "Entrar", text("#viewLogin h2"))
        js("localStorage.clear()")
    except Exception as exc:  # pragma: no cover - reporte de la prueba
        import traceback

        traceback.print_exc()
        check("ejecucion sin excepciones", False, repr(exc))
    finally:
        window.destroy()


def main():
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
        webview.start(run_steps, (window, controller))
    finally:
        for p in patches:
            p.stop()
    failed = [r for r in RESULTS if not r[1]]
    print(f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} verificaciones OK")
    sys.exit(1 if failed or not RESULTS else 0)


if __name__ == "__main__":
    main()
