# feature_extractor.py
# Features geometricas normalizadas a partir de los 21 landmarks de MediaPipe (sin x,y,z crudos).

from __future__ import annotations

import math
from typing import List, Optional, Sequence, Union

import numpy as np

# Indices MediaPipe Hands
_WRIST = 0
_THUMB_MCP, _THUMB_IP = 1, 2
_TIPS = (4, 8, 12, 16, 20)
_MCPS = (2, 5, 9, 13, 17)
_FINGER_NAMES = ("thumb", "index", "middle", "ring", "pinky")

Landmark = Union[dict, Sequence[float]]
Landmarks = List[Landmark]


def _xy(lm: Landmark) -> tuple[float, float]:
    if isinstance(lm, dict):
        return float(lm["x"]), float(lm["y"])
    return float(lm[0]), float(lm[1])


def _dist(a: Landmark, b: Landmark) -> float:
    ax, ay = _xy(a)
    bx, by = _xy(b)
    return math.hypot(ax - bx, ay - by)


def _hand_scale(lm: Landmarks) -> float:
    """Longitud de referencia: muñeca (0) -> MCP del dedo medio (9)."""
    return max(_dist(lm[_WRIST], lm[9]), 1e-4)


def _angle_between(v1: tuple[float, float], v2: tuple[float, float]) -> float:
    m1 = math.hypot(*v1)
    m2 = math.hypot(*v2)
    if m1 * m2 < 1e-9:
        return 0.0
    cos_a = max(-1.0, min(1.0, (v1[0] * v2[0] + v1[1] * v2[1]) / (m1 * m2)))
    return math.degrees(math.acos(cos_a))


def _finger_extended(lm: Landmarks, tip: int, mcp: int, scale: float) -> bool:
    """
    Dedo extendido: punta mas lejos de la muneca que el MCP (normalizado por escala de mano).
    """
    tip_wrist = _dist(lm[tip], lm[_WRIST]) / scale
    mcp_wrist = _dist(lm[mcp], lm[_WRIST]) / scale
    tip_mcp = _dist(lm[tip], lm[mcp]) / scale
    if tip_mcp < 0.22:
        return False
    return tip_wrist > mcp_wrist * 1.12 and tip_mcp > mcp_wrist * 0.85


def _thumb_extended(lm: Landmarks, scale: float) -> bool:
    tip_wrist = _dist(lm[4], lm[_WRIST]) / scale
    mcp_wrist = _dist(lm[_THUMB_MCP], lm[_WRIST]) / scale
    tip_mcp = _dist(lm[4], lm[_THUMB_IP]) / scale
    if tip_mcp < 0.18:
        return False
    return tip_wrist > mcp_wrist * 1.05 or tip_mcp > 0.38


def _inter_finger_angle(lm: Landmarks, tip_a: int, tip_b: int) -> float:
    """Angulo en la muneca entre vectores hacia dos puntas de dedo."""
    wx, wy = _xy(lm[_WRIST])
    ax, ay = _xy(lm[tip_a])
    bx, by = _xy(lm[tip_b])
    return _angle_between((ax - wx, ay - wy), (bx - wx, by - wy))


def _palm_orientation(lm: Landmarks) -> float:
    """Angulo de la palma: linea muneca -> MCP medio, en grados [-180, 180]."""
    wx, wy = _xy(lm[_WRIST])
    mx, my = _xy(lm[9])
    return math.degrees(math.atan2(my - wy, mx - wx))


def _thumb_cover_count(lm: Landmarks, scale: float) -> int:
    t4 = lm[4]
    tx, ty = _xy(t4)
    count = 0
    for pip_i, tip_i in ((6, 8), (10, 12), (14, 16), (18, 20)):
        tip, pip = lm[tip_i], lm[pip_i]
        px, py = _xy(pip)
        tx2, ty2 = _xy(tip)
        if (
            min(px, tx2) - scale * 0.1 <= tx <= max(px, tx2) + scale * 0.1
            and ty2 < ty - scale * 0.01
        ):
            count += 1
    return count


def _thumb_between_score(lm: Landmarks, scale: float) -> float:
    t4x, t4y = _xy(lm[4])
    i5x, i5y = _xy(lm[5])
    m9x, m9y = _xy(lm[9])
    lo = min(i5x, m9x) - scale * 0.12
    hi = max(i5x, m9x) + scale * 0.12
    if lo <= t4x <= hi:
        return 1.0
    return max(0.0, 1.0 - abs(t4x - (i5x + m9x) / 2) / (scale * 0.5))


# Nombres en el mismo orden que el vector devuelto por extract_features
FEATURE_NAMES: List[str] = [
    "finger_thumb",
    "finger_index",
    "finger_middle",
    "finger_ring",
    "finger_pinky",
    "angle_thumb_index",
    "angle_index_middle",
    "angle_middle_ring",
    "angle_ring_pinky",
    "dist_palm_thumb",
    "dist_palm_index",
    "dist_palm_middle",
    "dist_palm_ring",
    "dist_palm_pinky",
    "dist_thumb_index",
    "dist_thumb_middle",
    "palm_orientation",
    "index_middle_sep",
    "thumb_cover_norm",
    "four_fingers_up",
    "thumb_between",
    "extended_count_norm",
    "finger_spread",
    "palm_aspect",
    "fist_compactness",
]

N_FEATURES = len(FEATURE_NAMES)


def extract_features(hand_landmarks: Optional[Landmarks]) -> Optional[np.ndarray]:
    """
    Convierte 21 landmarks en un vector de 25 features geometricas normalizadas.

    Returns:
        np.ndarray float32 de forma (25,) o None si landmarks invalidos.
    """
    if not hand_landmarks or len(hand_landmarks) < 21:
        return None

    lm = hand_landmarks
    scale = _hand_scale(lm)

    thumb = 1.0 if _thumb_extended(lm, scale) else 0.0
    index = 1.0 if _finger_extended(lm, 8, 5, scale) else 0.0
    middle = 1.0 if _finger_extended(lm, 12, 9, scale) else 0.0
    ring = 1.0 if _finger_extended(lm, 16, 13, scale) else 0.0
    pinky = 1.0 if _finger_extended(lm, 20, 17, scale) else 0.0

    angle_ti = _inter_finger_angle(lm, 4, 8) / 180.0
    angle_im = _inter_finger_angle(lm, 8, 12) / 180.0
    angle_mr = _inter_finger_angle(lm, 12, 16) / 180.0
    angle_rp = _inter_finger_angle(lm, 16, 20) / 180.0

    dist_palm = [_dist(lm[t], lm[_WRIST]) / scale for t in _TIPS]
    dist_ti = _dist(lm[4], lm[8]) / scale
    dist_tm = _dist(lm[4], lm[12]) / scale
    palm_ori = _palm_orientation(lm) / 180.0

    # Separacion indice-medio (U vs V): angulo entre vectores MCP->tipa
    i5x, i5y = _xy(lm[5])
    i8x, i8y = _xy(lm[8])
    m9x, m9y = _xy(lm[9])
    m12x, m12y = _xy(lm[12])
    index_middle_sep = _angle_between((i8x - i5x, i8y - i5y), (m12x - m9x, m12y - m9y)) / 180.0

    cover = _thumb_cover_count(lm, scale) / 4.0
    four_up = 1.0 if (index and middle and ring and pinky) else 0.0
    thumb_between = _thumb_between_score(lm, scale)
    ext_count = (thumb + index + middle + ring + pinky) / 5.0

    tips_xy = [_xy(lm[t]) for t in _TIPS]
    spreads = []
    for i in range(len(tips_xy)):
        for j in range(i + 1, len(tips_xy)):
            spreads.append(math.hypot(tips_xy[i][0] - tips_xy[j][0], tips_xy[i][1] - tips_xy[j][1]))
    finger_spread = (sum(spreads) / len(spreads) / scale) if spreads else 0.0

    palm_w = _dist(lm[5], lm[17]) / scale
    palm_h = _dist(lm[_WRIST], lm[9]) / scale
    palm_aspect = palm_w / max(palm_h, 1e-4)

    non_thumb_dists = [_dist(lm[t], lm[_WRIST]) / scale for t in (8, 12, 16, 20)]
    fist_compact = sum(non_thumb_dists) / len(non_thumb_dists)

    vec = np.array(
        [
            thumb,
            index,
            middle,
            ring,
            pinky,
            angle_ti,
            angle_im,
            angle_mr,
            angle_rp,
            dist_palm[0],
            dist_palm[1],
            dist_palm[2],
            dist_palm[3],
            dist_palm[4],
            dist_ti,
            dist_tm,
            palm_ori,
            index_middle_sep,
            cover,
            four_up,
            thumb_between,
            ext_count,
            finger_spread,
            palm_aspect,
            fist_compact,
        ],
        dtype=np.float32,
    )
    return vec


def features_to_dict(features: np.ndarray) -> dict[str, float]:
    """Utilidad para depuracion / desempate."""
    if features is None or len(features) != N_FEATURES:
        return {}
    return {name: float(features[i]) for i, name in enumerate(FEATURE_NAMES)}
