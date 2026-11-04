# e2e_browser_hand.py
# Prueba de punta a punta de la version web en un navegador real (Microsoft Edge),
# con una camara simulada que muestra la seña L en un cuadro 16:9 (camara de laptop).
#
# Verifica que MediaPipe web cargue en el navegador, que los puntos se dibujen
# sobre la mano, que solo viajen los 21 puntos (no imagenes) y que el servidor
# reconozca la letra. Necesita MongoDB local encendido e internet (MediaPipe web).
#
#   python tests/e2e_browser_hand.py                 # usa Edge instalado
#   python tests/e2e_browser_hand.py --shot CAPTURA.png
#
# Codigo de salida 0 = todo OK.

import os
import subprocess
import sys
import tempfile
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import cv2  # noqa: E402
import numpy as np  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

PORT = 5077
BASE = f"http://127.0.0.1:{PORT}"
USER, PASSWORD = "zz_e2e_mano", "Secreto123!"
SHOT = sys.argv[sys.argv.index("--shot") + 1] if "--shot" in sys.argv else None
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append(ok)
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail and not ok else ""), flush=True)


def fake_camera_file(letter_png: str) -> str:
    """Video Y4M 1280x720 (16:9) con la imagen de la seña centrada."""
    img = cv2.imread(letter_png)
    frame = np.full((720, 1280, 3), 235, np.uint8)
    frame[:, 280:1000] = cv2.resize(img, (720, 720))
    yuv = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV_I420)
    path = os.path.join(tempfile.mkdtemp(prefix="cam_"), "senal.y4m")
    with open(path, "wb") as f:
        f.write(b"YUV4MPEG2 W1280 H720 F30:1 Ip A1:1 C420jpeg\n")
        for _ in range(30):
            f.write(b"FRAME\n" + yuv.tobytes())
    return path


def wait_health(timeout=90):
    end = time.time() + timeout
    while time.time() < end:
        try:
            with urllib.request.urlopen(BASE + "/health", timeout=2):
                return True
        except Exception:
            time.sleep(0.5)
    return False


def main():
    env = dict(os.environ, PORT=str(PORT), WEB_DEPLOYMENT="1")
    server = subprocess.Popen([sys.executable, "-W", "ignore", "web_server.py"], cwd=ROOT, env=env,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        check("servidor web arranca", wait_health())
        camera = fake_camera_file(os.path.join(ROOT, "src/gui_web/web/assets/letras/l.png"))
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="msedge", headless=True, args=[
                "--use-fake-ui-for-media-stream",
                "--use-fake-device-for-media-stream",
                f"--use-file-for-fake-video-capture={camera}",
            ])
            page = browser.new_page(viewport={"width": 1366, "height": 768})
            calls = []
            page.on("request", lambda r: calls.append(r.url.replace(BASE, "")) if "/api/" in r.url else None)
            page.goto(BASE + "/")
            page.wait_for_function("() => typeof tr === 'function' && !!window.__browserDeployment")

            page.evaluate("""async ([u, p]) => {
                await window.pywebview.api.register(u, p, p, false, false, false, 'medium', 'es');
                await window.pywebview.api.login(u, p, 'es');
            }""", [USER, PASSWORD])

            loaded = page.wait_for_function("() => browserHandLandmarkerLoading !== null && browserHandLandmarker", timeout=90000)
            check("MediaPipe web carga en el navegador", bool(loaded))

            page.evaluate("setView('aprendizaje')")
            page.wait_for_function("() => Array.isArray(latestHandPoints) && latestHandPoints.length === 21", timeout=30000)
            check("21 puntos de la mano detectados en el navegador", True)

            # Los puntos deben caer sobre la mano: dentro de la franja central donde esta la imagen.
            xs = page.evaluate("latestHandPoints.map(p => p[0])")
            check("puntos sobre la mano (franja central del video 16:9)",
                  all(280 / 1280 <= x <= 1000 / 1280 for x in xs), f"x={min(xs):.2f}..{max(xs):.2f}")

            painted = page.evaluate("""() => {
                const c = document.querySelector('#viewAprendizaje .hand-overlay');
                const d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;
                let n = 0; for(let i = 3; i < d.length; i += 4) if(d[i] > 0) n++;
                return n;
            }""")
            check("esqueleto dibujado sobre el video", painted > 500, f"pixeles={painted}")

            # Al servidor van los puntos del recorte central 4:3 del video (como una imagen
            # 640x480 del entrenamiento). Se calcula segun el tamaño real que entrego la camara.
            sent, shown, vw, vh = page.evaluate(
                "[browserLandmarks, latestHandPoints, browserCameraVideo.videoWidth, browserCameraVideo.videoHeight]")
            cw = min(vw, vh * 4 / 3)
            ch = min(vh, vw * 3 / 4)
            cx, cy = (vw - cw) / 2, (vh - ch) / 2
            expected = [((x * vw - cx) / cw, (y * vh - cy) / ch) for x, y in shown]
            check(f"puntos enviados en coordenadas 4:3 del entrenamiento (video {vw}x{vh})",
                  sent and all(abs(s[0] - e[0]) < 0.002 and abs(s[1] - e[1]) < 0.002 for s, e in zip(sent, expected)),
                  f"enviado={sent[0] if sent else None} esperado={expected[0]}")

            letter = None
            end = time.time() + 20
            while time.time() < end and letter != "L":
                letter = page.evaluate("window.pywebview.api.get_state().then(s => s.letter)")
                time.sleep(0.5)
            check("el servidor reconoce la letra L", letter == "L", f"letra={letter}")

            calls.clear()
            page.wait_for_timeout(2000)  # (time.sleep congelaria los eventos del navegador)
            frames = sum(1 for c in calls if c.startswith("/api/camera/frame"))
            points = sum(1 for c in calls if c.startswith("/api/camera/landmarks"))
            check("solo viajan los puntos, no imagenes", points > 3 and frames == 0, f"puntos={points} imagenes={frames}")
            check("envios limitados (~15 por segundo; ~1 ms de CPU cada uno)", points <= 40, f"puntos en 2 s={points}")

            if SHOT:
                page.wait_for_timeout(500)
                page.screenshot(path=SHOT)
            page.evaluate("window.pywebview.api.logout()")
            browser.close()
    finally:
        server.terminate()
        try:
            from src.database import DatabaseManager
            DatabaseManager()._users_collection().delete_one({"username": USER})
        except Exception:
            pass
    print(f"\n{sum(RESULTS)}/{len(RESULTS)} verificaciones OK")
    sys.exit(0 if RESULTS and all(RESULTS) else 1)


if __name__ == "__main__":
    main()
