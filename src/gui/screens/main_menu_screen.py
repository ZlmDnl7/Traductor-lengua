# main_menu_screen.py
# Menu principal tras iniciar sesion.
# Opciones: Traduccion, Cerrar sesion.

import tkinter as tk
from typing import Callable

import ttkbootstrap as ttk


class MainMenuScreen(ttk.Frame):
    """
    Menu principal: muestra nombre de usuario y botones
    para acceder a todas las opciones de la aplicacion.
    """

    def __init__(
        self,
        parent: tk.Misc,
        username: str,
        on_interaction: Callable[[], None],
        on_translation: Callable[[], None],
        on_voice: Callable[[], None],
        on_aprendizaje: Callable[[], None],
        on_logout: Callable[[], None],
        **kwargs
    ) -> None:
        super().__init__(parent, **kwargs)
        self._on_interaction = on_interaction
        self._on_translation = on_translation
        self._on_voice = on_voice
        self._on_aprendizaje = on_aprendizaje
        self._on_logout = on_logout
        self._username = username
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

        ttk.Label(card, text="Menú principal", font=("", 18, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(card, text=f"Bienvenido, {self._username}", font=("", 11)).grid(row=1, column=0, sticky="w", pady=(4, 18))

        ttk.Button(
            card,
            text="Interacción (Voz + Señas)",
            command=self._on_interaction,
            bootstyle="primary",
            width=32,
        ).grid(row=2, column=0, sticky="ew", pady=(0, 10))

        ttk.Button(
            card,
            text="Traducción en tiempo real",
            command=self._on_translation,
            bootstyle="info",
            width=32,
        ).grid(row=3, column=0, sticky="ew", pady=(0, 10))

        ttk.Button(
            card,
            text="Voz a texto",
            command=self._on_voice,
            bootstyle="success",
            width=32,
        ).grid(row=4, column=0, sticky="ew", pady=(0, 10))

        ttk.Button(
            card,
            text="Aprendizaje de señas",
            command=self._on_aprendizaje,
            bootstyle="warning",
            width=32,
        ).grid(row=5, column=0, sticky="ew", pady=(0, 20))

        ttk.Button(
            card,
            text="Cerrar sesión",
            command=self._on_logout,
            bootstyle="danger",
            width=32,
        ).grid(row=6, column=0, sticky="ew")
