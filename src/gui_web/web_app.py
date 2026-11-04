# web_app.py
# UI web embebida con PyWebView.

import os
from typing import Any


class WebApp:
    def __init__(self, controller: Any) -> None:
        self._controller = controller

    def run(self) -> None:
        import webview  # pywebview

        # Archivo HTML principal
        base_dir = os.path.dirname(os.path.abspath(__file__))
        html_path = os.path.join(base_dir, "web", "index.html")

        api = self._controller.get_web_api()

        window = webview.create_window(
            title="Enseñando",
            url=html_path,
            js_api=api,
            width=1280,
            height=720,
            min_size=(360, 600),
        )

        # Cierre limpio
        def on_closed():
            try:
                self._controller.on_app_close()
            except Exception:
                pass

        window.events.closed += on_closed

        webview.start(debug=False)

