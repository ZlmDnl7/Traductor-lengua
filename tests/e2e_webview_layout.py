# e2e_webview_layout.py
# Verifica que cada vista se vea completa sin scroll (ni vertical ni horizontal)
# en varios tamanos de pantalla, usando el motor real de PyWebView (WebView2).
# Base de datos en memoria y sin camara.
#
#   python tests/e2e_webview_layout.py                 # reporte
#   python tests/e2e_webview_layout.py --shots CARPETA # ademas guarda capturas
#
# Codigo de salida 0 = ninguna vista necesita scroll.

import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import webview  # noqa: E402

from tests.fakes import FakeAuth, FakeDB, controller_patches  # noqa: E402

SHOTS_DIR = sys.argv[sys.argv.index("--shots") + 1] if "--shots" in sys.argv else None
ONLY = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else None
# --a11y: mide con lectura accesible (texto grande) + espaciado para dislexia activados.
A11Y = "--a11y" in sys.argv

# Tamanos del area visible (CSS px): escritorio, laptop, tablet y celular.
SIZES = [(1920, 1080), (1366, 768), (1280, 720), (1024, 768), (768, 1024), (390, 844)]

# Vistas que no requieren sesion se miden antes de iniciar sesion.
PUBLIC_VIEWS = ["landing", "login", "register", "register_language", "register_accessibility"]
PRIVATE_VIEWS = ["menu", "profile", "settings", "interaction", "aprendizaje", "repaso", "reto",
                 "evaluacion_config", "evaluacion_run", "evaluacion_resultados", "evaluacion_historial", "faq"]

RESULTS = []

# Mide el desborde del documento y de cada elemento visible que se sale de la pantalla.
MEASURE_JS = """(() => {
  const se = document.scrollingElement;
  const out = {
    w: innerWidth, h: innerHeight,
    overY: Math.max(0, se.scrollHeight - innerHeight),
    overX: Math.max(0, se.scrollWidth - innerWidth),
    inner: [], offenders: [], view: null,
  };
  const view = [...document.querySelectorAll('main > section')].find(s => !s.classList.contains('hidden'));
  if(!view) return out;
  const vr = view.getBoundingClientRect();
  out.view = [view.id, Math.round(vr.top), Math.round(vr.bottom), Math.round(vr.height)];
  const label = el => (el.id || (typeof el.className === 'string' ? el.className : '') || el.tagName).toString().slice(0, 40);
  // Contenedores con scroll propio, dentro de la vista o por encima de ella (main, .app...).
  const scan = [...view.querySelectorAll('*'), view];
  for(let p = view.parentElement; p && p !== document.documentElement; p = p.parentElement) scan.push(p);
  // Listas que crecen con el uso (conversacion, historial) pueden desplazarse por dentro.
  const GROWING = '.chat, .evaluation-history-list, .faq-list';
  for(const el of scan){
    if(el.offsetParent === null && el !== document.body) continue;
    if(el.matches(GROWING)) continue;
    const cs = getComputedStyle(el);
    if(/(auto|scroll)/.test(cs.overflowY) && el.scrollHeight - el.clientHeight > 2 && el.tagName !== 'TEXTAREA'){
      out.inner.push(label(el) + ' +' + (el.scrollHeight - el.clientHeight));
    }
    if(/(auto|scroll)/.test(cs.overflowX) && el.scrollWidth - el.clientWidth > 2){
      out.inner.push(label(el) + ' x+' + (el.scrollWidth - el.clientWidth));
    }
  }
  // Elementos visibles (hojas) que quedan fuera de la pantalla.
  for(const el of view.querySelectorAll('*')){
    if(el.offsetParent === null || el.children.length) continue;
    if(el.closest(GROWING)) continue;
    const cs = getComputedStyle(el);
    if(cs.visibility === 'hidden' || cs.opacity === '0') continue;
    const r = el.getBoundingClientRect();
    if(r.width && r.height && (r.bottom > innerHeight + 1 || r.right > innerWidth + 1 || r.left < -1)){
      out.offenders.push(label(el));
      continue;
    }
    // Recortado por un contenedor con overflow oculto (no se ve aunque este "dentro" de la pantalla).
    for(let p = el.parentElement; p && p !== view.parentElement; p = p.parentElement){
      const pcs = getComputedStyle(p);
      if(pcs.overflowY === 'visible' && pcs.overflowX === 'visible') continue;
      if(p.matches(GROWING)) break;
      const pr = p.getBoundingClientRect();
      if(r.bottom > pr.bottom + 2 || r.right > pr.right + 2 || r.top < pr.top - 2){
        out.offenders.push('recortado:' + label(el));
      }
      break;
    }
  }
  out.offenders = [...new Set(out.offenders)].slice(0, 6);
  return out;
})()"""


def run(window, controller, db):
    # La app se carga dentro de un iframe del tamano exacto a medir: su viewport
    # (innerWidth/innerHeight y media queries) es el del iframe, sin depender del
    # tamano ni del escalado de la pantalla real.
    def top(code):
        return window.evaluate_js(code)

    def js(code):
        return top(f"document.getElementById('layoutFrame').contentWindow.eval({json.dumps(code)})")

    def wait(sec=0.5):
        time.sleep(sec)

    def open_frame(w, h):
        top(f"""(() => {{
            document.getElementById('layoutFrame')?.remove();
            const f = document.createElement('iframe');
            f.id = 'layoutFrame';
            f.src = location.href;
            const k = Math.min(1, innerWidth / {w}, innerHeight / {h});
            f.style.cssText = 'position:fixed;left:0;top:0;border:0;z-index:2147483647;background:#fff;'
              + 'width:{w}px;height:{h}px;transform-origin:0 0;transform:scale(' + k + ')';
            f.onload = () => {{ f.contentWindow.pywebview = window.pywebview; }};
            document.body.appendChild(f);
        }})()""")
        for _ in range(60):
            wait(0.25)
            if js("typeof tr === 'function' && !!window.pywebview && typeof setView === 'function'") is True:
                break
        wait(0.8)

    def prepare(view):
        """Pone cada vista en su estado mas cargado para medir el peor caso."""
        js(f"setView({json.dumps(view)})")
        if A11Y:
            js("accessibilitySettingsDirty = true; applyAccessibilityPreferences(false, true, false, true, 'large')")
        if view == "repaso":
            js("syncRepasoView && syncRepasoView()")
        elif view == "reto":
            controller.on_challenge_start()
        elif view == "faq":
            js("renderFaq(); document.querySelector('.faq-item').open = true")
        elif view == "evaluacion_historial":
            js("""(() => { for(let i = 0; i < 15; i++){
                saveEvaluationSession({duration_seconds: 60, score: (i * 7) % 23 - 6, hits: i % 5, errors: i % 3,
                  hit_letters: ['A','B','C','D','E'], error_letters: ['M','N']}); }
                renderEvaluationHistory(); })()""")
        elif view == "evaluacion_resultados":
            js("""(() => { for(const id of ['resultsHitLetters','resultsErrorLetters']){
                const el = document.getElementById(id); if(el) el.textContent = 'A, B, C, D, E, F, G, H'; } })()""")
        wait(0.8)

    def measure(view, w, h):
        m = js(MEASURE_JS)
        ok = m["overY"] <= 1 and m["overX"] <= 1 and not m["inner"] and not m["offenders"]
        RESULTS.append((view, w, h, ok, m))
        detail = "" if ok else f"  scrollY+{m['overY']} scrollX+{m['overX']} interno={m['inner']} fuera={m['offenders']} vista={m['view']}"
        print(f"{'OK  ' if ok else 'FAIL'} {w}x{h} {view}{detail}", flush=True)
        if SHOTS_DIR:
            from PIL import ImageGrab

            k = top("window.devicePixelRatio") or 1
            scale = top("Math.min(1, innerWidth / %d, innerHeight / %d)" % (w, h))
            x, y = window.x, window.y
            # Barra de titulo de la ventana: diferencia entre alto externo e interno.
            bar = window.height - top("innerHeight")
            gw, gh = int(w * scale), int(h * scale)
            ImageGrab.grab(bbox=(int(x * k), int((y + bar) * k), int((x + gw) * k), int((y + bar + gh) * k)),
                           all_screens=True).save(os.path.join(SHOTS_DIR, f"{w}x{h}-{view}.png"))

    try:
        for _ in range(40):
            if top("typeof tr === 'function' && !!window.pywebview && !!window.pywebview.api"):
                break
            time.sleep(0.25)
        top("localStorage.clear()")
        db._user("medidor")["learning_language"] = "es"
        db._user("medidor")["tutorial_completed"] = True
        top("pollTimer && clearInterval(pollTimer)")

        for (w, h) in SIZES:
            controller.web_logout()
            open_frame(w, h)
            for view in PUBLIC_VIEWS:
                if ONLY and view not in ONLY:
                    continue
                prepare(view)
                measure(view, w, h)

            controller.web_login("medidor", FakeAuth.PASSWORD, "es")
            controller.web_set_favorite_letter("A", True)
            controller.web_set_favorite_letter("B", True)
            for i in range(6):
                controller._web_messages.append({"who": "voice", "text": f"Mensaje de prueba número {i + 1} en la conversación"})
            open_frame(w, h)
            js("refreshFavoriteLetters && refreshFavoriteLetters()")
            wait(0.5)
            for view in PRIVATE_VIEWS:
                if ONLY and view not in ONLY:
                    continue
                prepare(view)
                measure(view, w, h)
    except Exception as exc:  # pragma: no cover - reporte
        import traceback

        traceback.print_exc()
        RESULTS.append(("excepcion", 0, 0, False, {"error": repr(exc)}))
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
        window = webview.create_window("e2e layout", url=html, js_api=api, width=1280, height=800,
                                       x=0, y=0, hidden=not SHOTS_DIR)
        webview.start(run, (window, controller, db))
    finally:
        for p in patches:
            p.stop()
    failed = [r for r in RESULTS if not r[3]]
    print(f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} vistas sin scroll")
    sys.exit(1 if failed or not RESULTS else 0)


if __name__ == "__main__":
    main()
