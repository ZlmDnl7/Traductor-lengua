# aprendizaje_screen.py
# Pantalla de aprendizaje visual para practicar señas.
# Solo muestra la referencia, la cámara en vivo y controles de navegación.

import tkinter as tk
from typing import Callable, Optional

import ttkbootstrap as ttk

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None


class AprendizajeScreen(ttk.Frame):
    """
    Pantalla de aprendizaje visual:
    - izquierda: referencia de la letra y texto grande
    - derecha: cámara en vivo y texto de instrucción
    - controles: Anterior, Siguiente
    """

    def __init__(
        self,
        parent: tk.Misc,
        on_back: Callable[[], None],
        **kwargs,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._on_back = on_back
        self._photo: Optional[any] = None
        self._build_ui()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = ttk.Frame(self, padding=(18, 14), bootstyle="light")
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(1, weight=1)

        ttk.Button(header, text="← Volver", command=self._on_back, bootstyle="secondary").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(header, text="Aprendizaje", font=("Segoe UI", 16, "bold")).grid(
            row=0, column=1, sticky="w", padx=(12, 0)
        )

        self._progress_var = tk.StringVar(value="A — 1/27")
        ttk.Label(header, textvariable=self._progress_var, font=("Segoe UI", 11, "bold"), bootstyle="primary").grid(
            row=1, column=1, sticky="w", padx=(12, 0), pady=(4, 0)
        )

        body = ttk.Frame(self, padding=(18, 12, 18, 18), bootstyle="light")
        body.grid(row=1, column=0, sticky="nsew")
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)

        split = ttk.Panedwindow(body, orient=tk.HORIZONTAL)
        split.grid(row=0, column=0, sticky="nsew")

        left = ttk.Frame(split, padding=18, bootstyle="light")
        right = ttk.Frame(split, padding=18, bootstyle="light")
        split.add(left, weight=2)
        split.add(right, weight=3)

        left.columnconfigure(0, weight=1)
        left.rowconfigure(1, weight=1)

        ref_frame = ttk.Labelframe(left, text="Referencia", padding=(16, 12), bootstyle="secondary")
        ref_frame.grid(row=0, column=0, sticky="nsew")
        ref_frame.columnconfigure(0, weight=1)
        ref_frame.rowconfigure(0, weight=1)

        self._reference_panel = ttk.Frame(ref_frame, padding=20, bootstyle="primary")
        self._reference_panel.grid(row=0, column=0, sticky="nsew")
        self._reference_panel.columnconfigure(0, weight=1)
        self._reference_panel.rowconfigure(0, weight=1)

        self._lbl_reference_letter = ttk.Label(
            self._reference_panel,
            text="A",
            font=("Segoe UI", 96, "bold"),
            bootstyle="inverse-primary",
            anchor=tk.CENTER,
        )
        self._lbl_reference_letter.grid(row=0, column=0, sticky="nsew")

        self._lbl_reference_name = ttk.Label(
            ref_frame,
            text="Letra de referencia",
            font=("Segoe UI", 15, "bold"),
            bootstyle="secondary",
        )
        self._lbl_reference_name.grid(row=1, column=0, sticky="ew", pady=(12, 0))

        right.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=1)

        cam_frame = ttk.Labelframe(right, text="Cámara", padding=(16, 12), bootstyle="secondary")
        cam_frame.grid(row=0, column=0, sticky="nsew")
        cam_frame.columnconfigure(0, weight=1)
        cam_frame.rowconfigure(0, weight=1)

        self._lbl_video = ttk.Label(
            cam_frame,
            text="Iniciando cámara…",
            anchor=tk.CENTER,
            bootstyle="secondary",
        )
        self._lbl_video.grid(row=0, column=0, sticky="nsew", pady=(0, 10))

        self._lbl_prompt = ttk.Label(
            cam_frame,
            text="Repite la seña",
            font=("Segoe UI", 18, "bold"),
            bootstyle="primary",
            anchor=tk.CENTER,
        )
        self._lbl_prompt.grid(row=1, column=0, sticky="ew", pady=(0, 12))

        actions = ttk.Frame(cam_frame)
        actions.grid(row=2, column=0, sticky="ew")
        actions.columnconfigure(0, weight=1)
        actions.columnconfigure(1, weight=1)

        ttk.Button(actions, text="Anterior", command=lambda: None, bootstyle="secondary").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Button(actions, text="Siguiente", command=lambda: None, bootstyle="primary").grid(
            row=0, column=1, sticky="e"
        )

    _DISPLAY_WIDTH = 640
    _DISPLAY_HEIGHT = 480

    def set_progress(self, letter: str, current: int, total: int) -> None:
        self._progress_var.set(f"{letter} — {current}/{total}")

    def set_reference_letter(self, letter: str) -> None:
        self._lbl_reference_letter.config(text=str(letter or "A"))

    def update_frame(self, image_bgr: any) -> None:
        if image_bgr is None:
            return
        if Image is None or ImageTk is None:
            self._lbl_video.config(text="Instale Pillow para ver el video: pip install Pillow")
            return
        try:
            import cv2

            h, w = image_bgr.shape[:2]
            if w != self._DISPLAY_WIDTH or h != self._DISPLAY_HEIGHT:
                image_bgr = cv2.resize(
                    image_bgr, (self._DISPLAY_WIDTH, self._DISPLAY_HEIGHT), interpolation=cv2.INTER_LINEAR
                )
            rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb)
            self._photo = ImageTk.PhotoImage(image=img)
            self._lbl_video.config(image=self._photo, text="")
            self._lbl_video.update_idletasks()
        except Exception as e:
            self._lbl_video.config(text=f"Error al mostrar el frame: {e}")

    def show_camera_error(self) -> None:
        self._lbl_video.config(
            text="No se pudo abrir la cámara. Verifique permisos y que no la use otra app."
        )

    def show_no_frames_error(self) -> None:
        self._lbl_video.config(
            text="La cámara no envía imágenes. Cierre Chrome/Zoom/Teams y reintente."
        )
