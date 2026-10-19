# motion_detector.py
# Detecta el trazo de movimiento de J (gancho con el menique) y Z (zigzag con el indice).
# El clasificador ML (SignClassifier) solo ve una postura estatica por frame, y estas dos
# letras del alfabeto dactilologico se definen por el MOVIMIENTO, no por la forma de la mano
# en un instante. Este modulo guarda un historial corto de posiciones de la punta del dedo
# y calcula si el trazo reciente coincide con el patron de J o de Z.
# En LIBRAS tambien detecta el movimiento de la Ç (forma de C + movimiento de la mano).
#
# Reutiliza los mismos umbrales que ya se validaron en gesture_classifier.py (clasificador
# legacy por reglas), pero de forma independiente para poder usarse junto al modelo ML.

from __future__ import annotations

import math
from collections import deque
from typing import Optional, Tuple

from .finger_analyzer import FingerState


class MotionDetector:
    """
    Rastrea la trayectoria de la punta del indice y del menique entre frames
    y detecta si describen el trazo de J o de Z.

    Uso tipico (una instancia por sesion de traduccion, se reinicia sola si
    cambia la postura de los dedos o si se llama a reset()):

        motion = MotionDetector()
        ...
        finger_state = FingerAnalyzer().analyze(landmarks)
        j_motion, z_motion = motion.update(finger_state)
    """

    # Frames consecutivos con trazo valido que se exigen antes de confirmar el
    # movimiento. Evita que el jitter normal de la camara al recien levantar el
    # dedo (que ya de por si mueve la punta un poco) se confunda con la seña.
    CONFIRM_FRAMES = 4

    def __init__(self, trail_len: int = 12, confirm_frames: int = CONFIRM_FRAMES) -> None:
        self._key: Optional[tuple] = None
        self._index_trail: deque = deque(maxlen=trail_len)
        self._pinky_trail: deque = deque(maxlen=trail_len)
        self._confirm_frames = confirm_frames
        self._j_streak = 0
        self._z_streak = 0
        # Trayectoria de la mano completa (no se reinicia al cambiar la postura de
        # los dedos, porque en la forma de C los dedos curvos oscilan entre frames).
        self._hand_trail: deque = deque(maxlen=trail_len)
        self._move_streak = 0
        self.cedilla_motion = False

    def reset(self) -> None:
        self._key = None
        self._index_trail.clear()
        self._pinky_trail.clear()
        self._j_streak = 0
        self._z_streak = 0
        self._hand_trail.clear()
        self._move_streak = 0
        self.cedilla_motion = False

    def update(self, finger_state: Optional[FingerState]) -> Tuple[bool, bool]:
        """
        Actualiza el historial con el frame actual y devuelve (j_motion, z_motion),
        confirmados solo si el patron se sostuvo varios frames seguidos.
        Si finger_state es None (no hay mano detectada) reinicia el historial.
        """
        if finger_state is None:
            self.reset()
            return False, False

        key = (finger_state.index, finger_state.middle, finger_state.ring, finger_state.pinky)
        if key != self._key:
            # Cambio de postura de dedos: el trazo anterior ya no es valido.
            self._key = key
            self._index_trail.clear()
            self._pinky_trail.clear()
            self._j_streak = 0
            self._z_streak = 0

        self._index_trail.append(finger_state.index_tip)
        self._pinky_trail.append(finger_state.pinky_tip)
        self._hand_trail.append(finger_state.index_tip)
        self._move_streak = self._move_streak + 1 if self._hand_moving(finger_state) else 0
        self.cedilla_motion = self._move_streak >= self._confirm_frames

        self._j_streak = self._j_streak + 1 if self._is_j(finger_state) else 0
        self._z_streak = self._z_streak + 1 if self._is_z(finger_state) else 0

        return self._j_streak >= self._confirm_frames, self._z_streak >= self._confirm_frames

    def _path_stats(self, trail: deque, pw: float) -> Tuple[float, float, float, int]:
        """Devuelve (rango_x, rango_y, distancia_total, cambios_de_direccion_en_x)."""
        if len(trail) < 2:
            return 0.0, 0.0, 0.0, 0
        xs = [p[0] for p in trail]
        ys = [p[1] for p in trail]
        total = 0.0
        for i in range(1, len(trail)):
            dx = trail[i][0] - trail[i - 1][0]
            dy = trail[i][1] - trail[i - 1][1]
            total += math.hypot(dx, dy)
        signs = []
        for i in range(1, len(trail)):
            dx = trail[i][0] - trail[i - 1][0]
            # Umbral de ruido: descarta micro-temblores de la deteccion de mano
            # que no representan un cambio de direccion intencional.
            if abs(dx) >= pw * 0.07:
                signs.append(1 if dx > 0 else -1)
        changes = sum(1 for i in range(1, len(signs)) if signs[i] != signs[i - 1])
        return max(xs) - min(xs), max(ys) - min(ys), total, changes

    def _is_j(self, f: FingerState) -> bool:
        """J: solo el menique extendido, con un gancho claro y sostenido de la punta."""
        pw = f.palm_width
        if not f.pinky or f.index or f.middle:
            return False
        xr, yr, total, _ = self._path_stats(self._pinky_trail, pw)
        if len(self._pinky_trail) < 6 or total < pw * 0.30:
            return False
        # El desplazamiento neto (xr/yr) debe ser una fraccion clara del recorrido total:
        # si el trazo es puro jitter (va y vuelve sin avanzar), el rango queda chico aunque
        # la distancia acumulada crezca.
        return (xr > pw * 0.20 or yr > pw * 0.20) and max(xr, yr) > total * 0.45

    def _hand_moving(self, f: FingerState) -> bool:
        """Ç (LIBRAS): la mano se desplaza de forma clara, no solo tiembla.
        La forma de C la decide el clasificador ML; aqui solo se mide el movimiento."""
        pw = f.palm_width
        xr, yr, total, _ = self._path_stats(self._hand_trail, pw)
        if len(self._hand_trail) < 6 or total < pw * 0.30:
            return False
        return max(xr, yr) > pw * 0.20 and max(xr, yr) > total * 0.45

    def _is_z(self, f: FingerState) -> bool:
        """Z: solo el indice extendido y hacia arriba, con un zigzag horizontal real
        (ida y vuelta, al menos 2 cambios de direccion), no solo un desplazamiento."""
        pw = f.palm_width
        if not f.index or not f.index_up:
            return False
        xr, yr, total, changes = self._path_stats(self._index_trail, pw)
        if len(self._index_trail) < 7 or total < pw * 0.45:
            return False
        return xr > pw * 0.28 and changes >= 2
