# e2e_webview_tutorial.py
# Prueba de punta a punta del tutorial de bienvenida en el motor real de PyWebView,
# con una base de datos en memoria y sin camara.
#
#   python tests/e2e_webview_tutorial.py
#   python tests/e2e_webview_tutorial.py --shots CARPETA   # ventana visible + capturas
#
# Codigo de salida 0 = todo OK.

import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import webview  # noqa: E402

from tests.fakes import FakeAuth, FakeDB, controller_patches  # noqa: E402

RESULTS = []
SHOTS_DIR = sys.argv[sys.argv.index("--shots") + 1] if "--shots" in sys.argv else None


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

    def tour_visible():
        return not js("document.getElementById('tour').classList.contains('hidden')")

    def spotlight_on(sel):
        return js(f"""(() => {{
            const t = document.querySelector({json.dumps(sel)}).getBoundingClientRect();
            const s = document.getElementById('tourSpotlight').getBoundingClientRect();
            return !document.getElementById('tour').classList.contains('no-target')
              && s.left <= t.left && s.top <= t.top && s.right >= t.right && s.bottom >= t.bottom;
        }})()""")

    def card_inside():
        return js("""(() => { const c = document.getElementById('tourCard').getBoundingClientRect();
            return c.left >= 0 && c.top >= 0 && c.right <= innerWidth && c.bottom <= innerHeight; })()""")

    def shot(name):
        if not SHOTS_DIR:
            return
        from PIL import ImageGrab

        wait(0.6)
        k = js("window.devicePixelRatio") or 1
        x, y = window.x, window.y
        ImageGrab.grab(bbox=(int(x * k), int(y * k), int((x + window.width) * k), int((y + window.height) * k)),
                       all_screens=True).save(os.path.join(SHOTS_DIR, name))

    try:
        for _ in range(40):
            if js("typeof tr === 'function' && !!window.pywebview && !!window.pywebview.api"):
                break
            time.sleep(0.25)
        js("localStorage.clear()")

        # ===== Usuario nuevo: el tutorial aparece solo =====
        db._user("nuevo")["tutorial_completed"] = False
        js(f"document.getElementById('loginUser').value='nuevo'; document.getElementById('loginPass').value='{FakeAuth.PASSWORD}'")
        click("#btnLogin")
        wait(1.5)
        check("usuario nuevo: tutorial visible", tour_visible())
        check("paso 1: bienvenida con el nombre", "nuevo" in text("#tourTitle"), text("#tourTitle"))
        check("paso 1: progreso", text("#tourProgress") == "Paso 1 de 10", text("#tourProgress"))
        check("paso 1: sin boton Anterior", js("document.getElementById('tourPrev').classList.contains('hidden')"))
        shot("1-bienvenida.png")

        click("#tourNext")
        check("paso 2: resalta el selector de idioma", spotlight_on(".lang-switch"))
        click("#tourNext")
        check("paso 3: resalta Aprendizaje", spotlight_on("#btnOpenAprendizaje"), text("#tourTitle"))
        shot("2-aprendizaje.png")
        click("#tourPrev")
        check("Anterior vuelve al paso 2", text("#tourProgress") == "Paso 2 de 10", text("#tourProgress"))

        expected = ["#btnOpenAprendizaje", "#btnOpenRepaso", "#btnOpenReto", "#btnOpenEvaluacion",
                    "#btnOpenEvaluacionHistorial", "#btnOpenInteraction", "#btnOpenSettings"]
        for sel in expected:
            click("#tourNext")
            check(f"resalta {sel}", spotlight_on(sel), text("#tourTitle"))
            check(f"tarjeta completa en pantalla ({sel})", card_inside())
        shot("3-configuracion.png")

        click("#tourNext")
        check("ultimo paso: consejos", text("#tourProgress") == "Paso 10 de 10", text("#tourProgress"))
        check("ultimo paso: boton Empezar", text("#tourNext") == "¡Empezar!", text("#tourNext"))
        check("ultimo paso: sin Omitir", js("document.getElementById('tourSkip').classList.contains('hidden')"))
        shot("4-consejos.png")
        click("#tourNext")
        check("al terminar se cierra", not tour_visible())
        check("al terminar se guarda en la base", db._user("nuevo").get("tutorial_completed") is True)
        wait(1.5)
        check("no se vuelve a abrir solo", not tour_visible())

        # ===== Repetir desde el menu, en ingles, y salir con Escape =====
        js("""(() => { const i=document.querySelector('input[name="menuLearningLanguage"][value="en"]');
            i.checked=true; i.dispatchEvent(new Event('change')); })()""")
        wait(1.5)
        click("#btnOpenTutorial")
        check("Ver tutorial lo reabre", tour_visible())
        check("tutorial en ingles", text("#tourNext") == "Next" and text("#tourProgress") == "Step 1 of 10",
              f"{text('#tourNext')} / {text('#tourProgress')}")
        js("document.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape'}))")
        wait()
        check("Escape lo cierra", not tour_visible())

        # ===== Usuario existente (sin el campo): no ve el tutorial =====
        click("#btnLogout")
        js(f"document.getElementById('loginUser').value='antiguo'; document.getElementById('loginPass').value='{FakeAuth.PASSWORD}'")
        click("#btnLogin")
        wait(1.5)
        check("usuario existente: sin tutorial", not tour_visible())
        click("#btnLogout")
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
        window = webview.create_window("e2e tutorial", url=html, js_api=api, width=1280, height=800,
                                       x=40, y=40, hidden=not SHOTS_DIR)
        webview.start(run_steps, (window, controller, db))
    finally:
        for p in patches:
            p.stop()
    failed = [r for r in RESULTS if not r[1]]
    print(f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} verificaciones OK")
    sys.exit(1 if failed or not RESULTS else 0)


if __name__ == "__main__":
    main()
