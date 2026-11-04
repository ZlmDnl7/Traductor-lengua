# login_screen.py
# Pantalla de inicio de sesion.
# Responsabilidad unica: capturar credenciales y notificar resultado.

import tkinter as tk
from typing import Callable, Optional

import ttkbootstrap as ttk


class LoginScreen(ttk.Frame):
    """
    Formulario de login: usuario, contrasena, boton Entrar y enlace a Registro.
    Comunicacion mediante callbacks (bajo acoplamiento).
    """

    def __init__(
        self,
        parent: tk.Misc,
        on_login: Callable[[str, str], None],
        on_go_register: Callable[[], None],
        **kwargs
    ) -> None:
        super().__init__(parent, **kwargs)
        self._on_login = on_login
        self._on_go_register = on_go_register
        self._build_ui()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        container = ttk.Frame(self, padding=40)
        container.grid(row=0, column=0, sticky="nsew")
        container.columnconfigure(0, weight=1)

        card = ttk.Frame(container, padding=30, bootstyle="light")
        card.grid(row=0, column=0, sticky="n", padx=10, pady=10)
        card.columnconfigure(0, weight=1)

        ttk.Label(card, text="Enseñando", font=("", 18, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(card, text="Inicia sesión para continuar", font=("", 11)).grid(row=1, column=0, sticky="w", pady=(4, 18))

        ttk.Label(card, text="Usuario").grid(row=2, column=0, sticky="w")
        self._username_var = tk.StringVar()
        self._entry_user = ttk.Entry(card, textvariable=self._username_var, width=34)
        self._entry_user.grid(row=3, column=0, sticky="ew", pady=(4, 14))

        ttk.Label(card, text="Contraseña").grid(row=4, column=0, sticky="w")
        self._password_var = tk.StringVar()
        self._entry_pass = ttk.Entry(card, textvariable=self._password_var, show="*", width=34)
        self._entry_pass.grid(row=5, column=0, sticky="ew", pady=(4, 18))

        btn_frame = ttk.Frame(card)
        btn_frame.grid(row=6, column=0, sticky="ew")
        ttk.Button(btn_frame, text="Entrar", command=self._do_login, bootstyle="primary").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="Crear cuenta", command=self._on_go_register, bootstyle="secondary").pack(side=tk.LEFT)

        self._lbl_error = ttk.Label(card, text="", bootstyle="danger")
        self._lbl_error.grid(row=7, column=0, sticky="w", pady=(14, 0))

    def _do_login(self) -> None:
        user = self._username_var.get().strip()
        pwd = self._password_var.get()
        if not user:
            self._show_error("Ingrese su usuario")
            return
        if not pwd:
            self._show_error("Ingrese su contrasena")
            return
        self._lbl_error.config(text="")
        self._on_login(user, pwd)

    def _show_error(self, msg: str) -> None:
        self._lbl_error.config(text=msg)

    def show_error(self, msg: str) -> None:
        """Permite al controlador mostrar errores de autenticacion."""
        self._show_error(msg)

    def clear_error(self) -> None:
        self._lbl_error.config(text="")
