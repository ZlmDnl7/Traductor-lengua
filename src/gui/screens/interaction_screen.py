# interaction_screen.py
# Pantalla unificada: interacción voz ↔ señas (una sola vista).

import tkinter as tk
from typing import Callable, Optional

import ttkbootstrap as ttk
try:
    # ttkbootstrap >= 2.0 movio ScrolledFrame a widgets.scrolled
    from ttkbootstrap.widgets.scrolled import ScrolledFrame
except ImportError:
    # ttkbootstrap 1.x
    from ttkbootstrap.scrolled import ScrolledFrame

class InteractionScreen(ttk.Frame):
    """
    Vista unificada para comunicación:
    - Panel izquierdo: cámara + letra detectada + buffer de palabra (señas)
    - Panel derecho: voz a texto + historial tipo chat
    """

    def __init__(
        self,
        parent: tk.Misc,
        on_back: Callable[[], None],
        on_voice_start: Callable[[], None],
        on_voice_stop: Callable[[], None],
        on_clear_sign_buffer: Callable[[], None],
        on_sign_space: Callable[[], None],
        on_sign_backspace: Callable[[], None],
        on_sign_send: Callable[[], None],
        **kwargs,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._on_back = on_back
        self._on_voice_start = on_voice_start
        self._on_voice_stop = on_voice_stop
        self._on_clear_sign_buffer = on_clear_sign_buffer
        self._on_sign_space = on_sign_space
        self._on_sign_backspace = on_sign_backspace
        self._on_sign_send = on_sign_send

        self._photo: Optional[any] = None
        self._voice_capturing = False
        self._build_ui()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = ttk.Frame(self, padding=(18, 14), bootstyle="light")
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(1, weight=1)

        ttk.Button(header, text="← Menú", command=self._on_back_if_idle, bootstyle="secondary").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(header, text="Interacción", font=("Segoe UI", 16, "bold")).grid(
            row=0, column=1, sticky="w", padx=(12, 0)
        )
        ttk.Label(header, text="Voz + Señas en una sola pantalla", font=("Segoe UI", 10)).grid(
            row=1, column=1, sticky="w", padx=(12, 0), pady=(2, 0)
        )

        root = ttk.Frame(self, padding=(18, 12, 18, 18), bootstyle="light")
        root.grid(row=1, column=0, sticky="nsew")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # ttkbootstrap expone el widget como Panedwindow (no PanedWindow)
        paned = ttk.Panedwindow(root, orient=tk.HORIZONTAL)
        paned.grid(row=0, column=0, sticky="nsew")

        left = ttk.Frame(paned, padding=8, bootstyle="light")
        right = ttk.Frame(paned, padding=8, bootstyle="light")
        paned.add(left, weight=3)
        paned.add(right, weight=2)

        # Panel señas/cámara
        left.columnconfigure(0, weight=1)
        left.rowconfigure(1, weight=1)

        lf_sign = ttk.Labelframe(left, text="Señas → Texto", padding=14, bootstyle="secondary")
        lf_sign.grid(row=0, column=0, sticky="nsew")
        lf_sign.columnconfigure(0, weight=1)
        lf_sign.rowconfigure(1, weight=1)

        self._lbl_video = ttk.Label(
            lf_sign,
            text="Iniciando cámara…",
            anchor=tk.CENTER,
            bootstyle="secondary",
        )
        self._lbl_video.grid(row=1, column=0, sticky="nsew", pady=(10, 10))

        self._lbl_letter = ttk.Label(
            lf_sign,
            text="Letra: -",
            font=("Segoe UI", 28, "bold"),
            bootstyle="primary",
            anchor=tk.CENTER,
        )
        self._lbl_letter.grid(row=2, column=0, sticky="ew", pady=(0, 10))

        buffer_row = ttk.Frame(lf_sign)
        buffer_row.grid(row=3, column=0, sticky="ew")
        buffer_row.columnconfigure(0, weight=1)

        ttk.Label(buffer_row, text="Texto (señas):", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w")
        self._sign_text_var = tk.StringVar(value="")
        self._ent_sign = ttk.Entry(buffer_row, textvariable=self._sign_text_var, state="readonly", font=("Segoe UI", 11))
        self._ent_sign.grid(row=1, column=0, sticky="ew", pady=(6, 0))

        sign_actions = ttk.Frame(lf_sign)
        sign_actions.grid(row=4, column=0, sticky="ew", pady=(10, 0))
        sign_actions.columnconfigure(3, weight=1)

        ttk.Button(sign_actions, text="Espacio", command=self._on_sign_space, bootstyle="secondary").grid(row=0, column=0, padx=(0, 8))
        ttk.Button(sign_actions, text="Borrar", command=self._on_sign_backspace, bootstyle="secondary").grid(row=0, column=1, padx=(0, 8))
        ttk.Button(sign_actions, text="Limpiar", command=self._on_clear_sign_buffer, bootstyle="danger-outline").grid(row=0, column=2, padx=(0, 8))
        ttk.Button(sign_actions, text="Enviar señas", command=self._on_sign_send, bootstyle="success").grid(row=0, column=4, sticky="e")

        # Panel voz/chat
        right.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=1)

        lf_voice = ttk.Labelframe(right, text="Voz → Texto", padding=14, bootstyle="secondary")
        lf_voice.grid(row=0, column=0, sticky="nsew")
        lf_voice.columnconfigure(0, weight=1)

        self._btn_voice = ttk.Button(
            lf_voice,
            text="Grabar",
            command=self._toggle_voice,
            bootstyle="primary",
        )
        self._btn_voice.grid(row=0, column=0, sticky="w", pady=(2, 6))

        self._lbl_voice_status = ttk.Label(lf_voice, text="", bootstyle="secondary")
        self._lbl_voice_status.grid(row=1, column=0, sticky="w", pady=(0, 8))

        ttk.Label(lf_voice, text="Conversación", font=("Segoe UI", 10, "bold")).grid(
            row=2, column=0, sticky="w", pady=(10, 6)
        )

        # Chat estilo “burbujas” (mejor UX que un textarea)
        self._chat_sf = ScrolledFrame(lf_voice, autohide=True, bootstyle="light")
        self._chat_sf.grid(row=3, column=0, sticky="nsew")
        lf_voice.rowconfigure(3, weight=1)
        self._chat_sf.columnconfigure(0, weight=1)

        self._chat_container = ttk.Frame(self._chat_sf, bootstyle="light")
        self._chat_container.grid(row=0, column=0, sticky="nsew")
        self._chat_container.columnconfigure(0, weight=1)
        self._chat_row = 0

        self._lbl_error = ttk.Label(lf_voice, text="", bootstyle="danger", wraplength=520)
        self._lbl_error.grid(row=4, column=0, sticky="w", pady=(10, 0))

    def _on_back_if_idle(self) -> None:
        # Bloquea volver mientras está grabando (evita estados raros)
        if self._voice_capturing:
            return
        self._on_back()

    # ========= Señal de cámara =========
    _DISPLAY_WIDTH = 640
    _DISPLAY_HEIGHT = 480

    def update_frame(self, image_bgr: any) -> None:
        if image_bgr is None:
            return
        try:
            from PIL import Image, ImageTk
        except Exception:
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

    def update_letter(self, letter: Optional[str]) -> None:
        self._lbl_letter.config(text=f"Letra: {letter}" if letter else "Letra: -")

    def show_camera_error(self) -> None:
        self._lbl_video.config(
            text="No se pudo abrir la cámara. Verifique permisos y que no la use otra app."
        )

    def show_no_frames_error(self) -> None:
        self._lbl_video.config(
            text="La cámara no envía imágenes. Cierre Chrome/Zoom/Teams y reintente."
        )

    def set_sign_text(self, text: str) -> None:
        self._ent_sign.config(state="normal")
        self._sign_text_var.set(text)
        self._ent_sign.config(state="readonly")

    def append_chat(self, who: str, text: str) -> None:
        if not text:
            return
        who_lower = (who or "").lower()
        is_me = ("voz" in who_lower) or who_lower.startswith("yo")
        is_other = ("seña" in who_lower) or ("sen" in who_lower)

        bubble_style = "primary" if is_me else ("success" if is_other else "secondary")
        anchor = "e" if is_me else "w"

        row = ttk.Frame(self._chat_container, bootstyle="light")
        row.grid(row=self._chat_row, column=0, sticky="ew", pady=6)
        row.columnconfigure(0, weight=1)

        bubble = ttk.Frame(row, padding=(10, 8), bootstyle=bubble_style)
        bubble.grid(row=0, column=0, sticky=anchor)

        ttk.Label(bubble, text=who, font=("Segoe UI", 9, "bold"), bootstyle="inverse-" + bubble_style).grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            bubble,
            text=text,
            font=("Segoe UI", 11),
            wraplength=360,
            justify=tk.LEFT,
            bootstyle="inverse-" + bubble_style,
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        self._chat_row += 1
        try:
            self._chat_sf.yview_moveto(1.0)
        except Exception:
            pass

    # ========= Voz =========
    def _toggle_voice(self) -> None:
        self._lbl_error.config(text="")
        if not self._voice_capturing:
            self._voice_capturing = True
            self._btn_voice.config(text="Detener", bootstyle="danger", state=tk.NORMAL)
            self._lbl_voice_status.config(text="Grabando…")
            self._on_voice_start()
        else:
            self._btn_voice.config(state=tk.DISABLED)
            self._lbl_voice_status.config(text="Transcribiendo…")
            self._on_voice_stop()

    def voice_done(self) -> None:
        self._voice_capturing = False
        self._btn_voice.config(text="Grabar", bootstyle="primary", state=tk.NORMAL)
        self._lbl_voice_status.config(text="Listo.")
        self._lbl_error.config(text="")

    def voice_error(self, msg: str) -> None:
        msg = str(msg).strip()
        # Mensaje corto para UX; los tracebacks ya no son necesarios en modo normal.
        self._lbl_error.config(text=msg if msg else "Repite nuevamente.")

