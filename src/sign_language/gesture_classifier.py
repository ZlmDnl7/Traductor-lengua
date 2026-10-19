# gesture_classifier.py
# Clasifica A-Z comparando la mano con las 26 reglas y eligiendo la mejor coincidencia.

from typing import Callable, Dict, List, Optional, Tuple

from .finger_analyzer import FingerState
from .motion_detector import MotionDetector

ScoreFn = Callable[[FingerState, bool, bool], float]


class GestureClassifier:
    """Evalua las 26 letras y devuelve la de mayor puntuacion."""

    MIN_SCORE = 38.0
    MIN_MARGIN = 5.0

    def __init__(self) -> None:
        self._last_letter: Optional[str] = None
        self._stability_count = 0
        try:
            from src.config import SIGN_STABILITY_FRAMES
            self._STABILITY_THRESHOLD = max(4, int(SIGN_STABILITY_FRAMES) - 2)
        except Exception:
            self._STABILITY_THRESHOLD = 6

        self._motion = MotionDetector()
        self._scorers: Dict[str, ScoreFn] = self._build_scorers()

    def _reset_motion(self) -> None:
        self._motion.reset()

    def _update_motion(self, f: FingerState) -> Tuple[bool, bool]:
        return self._motion.update(f)

    def _add(self, score: float, cond: bool, pts: float) -> float:
        return score + (pts if cond else 0.0)

    def _pen(self, score: float, cond: bool, pts: float) -> float:
        return score - (pts if cond else 0.0)

    def _build_scorers(self) -> Dict[str, ScoreFn]:
        def score_A(f, j, z):
            s = 0.0
            s = self._add(s, f.fist_closed, 35)
            s = self._add(s, not f.index and not f.middle, 30)
            s = self._add(s, f.thumb_side or f.thumb_position == "side", 35)
            s = self._add(s, f.finger_compact, 15)
            s = self._pen(s, f.circle_closed and f.thumb_index_touch, 50)
            s = self._pen(s, f.has_inner_gap and f.thumb_index_touch, 45)
            s = self._pen(s, f.thumb_over or f.thumb_cover_count >= 2, 45)
            s = self._pen(s, f.thumb_between, 40)
            s = self._pen(s, f.four_fingers_up, 55)
            s = self._pen(s, f.index or f.middle, 25)
            return s

        def score_B(f, j, z):
            s = 0.0
            s = self._add(s, f.four_fingers_up, 55)
            s = self._add(s, f.palm_frontal, 20)
            s = self._add(s, not f.thumb_between, 20)
            s = self._pen(s, f.thumb_between and f.index and f.middle, 50)
            s = self._pen(s, f.thumb_index_touch, 35)
            s = self._pen(s, f.index and f.middle and not f.ring, 40)
            return s

        def score_C(f, j, z):
            s = 0.0
            s = self._add(s, f.open_curve, 40)
            s = self._add(s, f.extended_count >= 3 and not f.thumb_index_touch, 25)
            s = self._pen(s, f.thumb_index_touch, 55)
            s = self._pen(s, f.circle_closed and f.has_inner_gap, 30)
            s = self._pen(s, f.four_fingers_up, 45)
            s = self._pen(s, f.palm_down, 20)
            return s

        def score_D(f, j, z):
            s = 0.0
            s = self._add(s, f.index and f.index_up, 45)
            s = self._add(s, f.thumb_middle_touch or f.circle_small, 40)
            s = self._add(s, not f.index_bent, 15)
            s = self._add(s, not f.thumb_index_touch or not (f.middle and f.ring and f.pinky), 10)
            s = self._pen(s, f.thumb_index_touch and f.middle and f.ring and f.pinky, 55)
            s = self._pen(s, not f.index, 50)
            return s

        def score_E(f, j, z):
            s = 0.0
            s = self._add(s, f.fist_closed, 30)
            s = self._add(s, f.thumb_position == "inside_top", 35)
            s = self._pen(s, f.thumb_side, 30)
            s = self._pen(s, f.index, 20)
            return s

        def score_F(f, j, z):
            s = 0.0
            s = self._add(s, f.thumb_index_touch, 50)
            s = self._add(s, f.index, 25)
            s = self._add(s, (f.middle and f.ring) or (f.middle and f.pinky) or (f.ring and f.pinky), 35)
            s = self._pen(s, not f.thumb_index_touch, 55)
            s = self._pen(s, f.four_fingers_up, 50)
            s = self._pen(s, f.open_curve and not f.thumb_index_touch, 35)
            return s

        def score_G(f, j, z):
            s = 0.0
            s = self._add(s, f.thumb and f.index and not f.middle and not f.ring and not f.pinky, 45)
            s = self._add(s, f.index_horizontal or f.gesture_direction == "horizontal", 35)
            s = self._pen(s, f.middle or f.ring or f.pinky, 55)
            s = self._pen(s, f.open_curve or f.has_inner_gap, 45)
            s = self._pen(s, f.four_fingers_up, 50)
            s = self._pen(s, f.circle_closed, 40)
            s = self._pen(s, f.fist_closed and not f.index_horizontal, 35)
            return s

        def score_H(f, j, z):
            s = 0.0
            s = self._add(s, f.index and f.middle, 30)
            s = self._add(s, f.two_finger_pose == "horizontal", 35)
            s = self._add(s, not f.ring and not f.pinky, 20)
            return s

        def score_I(f, j, z):
            s = 0.0
            s = self._add(s, f.pinky and not f.index and not f.middle, 40)
            s = self._add(s, not f.ring, 20)
            s = self._pen(s, j, 55)
            s = self._pen(s, f.thumb and not f.pinky, 15)
            return s

        def score_J(f, j, z):
            s = 0.0
            s = self._add(s, f.pinky and not f.index and not f.middle, 25)
            s = self._add(s, j, 55)
            s = self._pen(s, not j, 60)
            return s

        def score_K(f, j, z):
            s = 0.0
            s = self._add(s, f.index and f.middle and not f.ring and not f.pinky, 35)
            s = self._add(s, f.thumb_between or (f.thumb and f.two_finger_pose in ("apart_up", "together_up")), 35)
            s = self._add(s, f.index_up or f.two_finger_pose == "apart_up", 20)
            s = self._pen(s, f.ring or f.pinky, 65)
            s = self._pen(s, f.four_fingers_up, 60)
            s = self._pen(s, f.palm_down and f.index_down, 35)
            return s

        def score_L(f, j, z):
            s = 0.0
            s = self._add(s, f.thumb and f.index, 30)
            s = self._add(s, f.index_up, 25)
            s = self._add(s, not f.middle and not f.ring and not f.pinky, 25)
            s = self._pen(s, f.index_horizontal, 30)
            s = self._pen(s, z, 40)
            return s

        def score_M(f, j, z):
            s = 0.0
            s = self._add(s, f.fist_closed, 25)
            s = self._add(s, f.thumb_cover_count >= 3 or f.thumb_position == "inside_over3", 45)
            s = self._pen(s, f.pinky, 35)
            s = self._pen(s, f.thumb_side, 40)
            s = self._pen(s, f.circle_closed, 35)
            return s

        def score_N(f, j, z):
            s = 0.0
            s = self._add(s, f.fist_closed, 25)
            s = self._add(s, f.thumb_cover_count == 2 or f.thumb_position == "inside_over2", 45)
            s = self._pen(s, f.thumb_cover_count >= 3, 40)
            s = self._pen(s, f.thumb_side, 35)
            s = self._pen(s, f.pinky, 25)
            return s

        def score_O(f, j, z):
            s = 0.0
            s = self._add(s, f.circle_closed or (f.thumb_index_touch and f.has_inner_gap and f.fist_closed), 50)
            s = self._add(s, f.has_inner_gap and not f.four_fingers_up, 25)
            s = self._pen(s, f.thumb_over, 40)
            s = self._pen(s, f.four_fingers_up, 50)
            s = self._pen(s, f.index and f.middle and f.ring and f.index_up, 40)
            return s

        def score_P(f, j, z):
            s = 0.0
            s = self._add(s, f.index and f.middle, 20)
            s = self._add(s, f.thumb_between, 25)
            s = self._add(s, f.palm_down or f.index_down or f.gesture_direction == "down", 40)
            s = self._pen(s, f.index_up and f.palm_frontal, 35)
            s = self._pen(s, f.two_finger_pose == "horizontal", 30)
            return s

        def score_Q(f, j, z):
            s = 0.0
            s = self._add(s, f.thumb and f.index, 25)
            s = self._add(s, f.palm_down or f.index_down, 40)
            s = self._pen(s, f.index_horizontal, 25)
            return s

        def score_R(f, j, z):
            s = 0.0
            s = self._add(s, f.index and f.middle, 30)
            s = self._add(s, f.two_finger_pose == "crossed", 45)
            return s

        def score_S(f, j, z):
            s = 0.0
            s = self._add(s, f.fist_closed, 30)
            s = self._add(s, f.thumb_over or f.thumb_position == "inside_front", 45)
            s = self._pen(s, f.thumb_side, 45)
            s = self._pen(s, f.thumb_between, 40)
            s = self._pen(s, f.thumb_cover_count >= 3, 25)
            return s

        def score_T(f, j, z):
            s = 0.0
            s = self._add(s, f.fist_closed, 25)
            s = self._add(s, f.thumb_between, 45)
            s = self._pen(s, f.thumb_over, 35)
            s = self._pen(s, f.thumb_side, 35)
            return s

        def score_U(f, j, z):
            s = 0.0
            s = self._add(s, f.index and f.middle and not f.ring and not f.pinky, 35)
            s = self._add(s, f.two_finger_pose == "together_up", 30)
            s = self._add(s, not f.thumb, 15)
            s = self._pen(s, f.ring or f.pinky, 50)
            s = self._pen(s, f.two_finger_pose == "apart_up", 25)
            return s

        def score_V(f, j, z):
            s = 0.0
            s = self._add(s, f.index and f.middle and not f.ring and not f.pinky, 35)
            s = self._add(s, f.two_finger_pose == "apart_up", 35)
            s = self._pen(s, f.ring or f.pinky, 50)
            s = self._pen(s, f.thumb, 15)
            return s

        def score_W(f, j, z):
            s = 0.0
            s = self._add(s, f.index and f.middle and f.ring, 40)
            s = self._add(s, not f.pinky, 20)
            s = self._pen(s, f.thumb, 15)
            return s

        def score_X(f, j, z):
            s = 0.0
            s = self._add(s, f.index and f.index_bent, 45)
            s = self._add(s, not f.middle and not f.ring and not f.pinky, 25)
            s = self._pen(s, f.index and not f.index_bent, 30)
            return s

        def score_Y(f, j, z):
            s = 0.0
            s = self._add(s, f.thumb and f.pinky, 45)
            s = self._add(s, not f.index and not f.middle, 25)
            return s

        def score_Z(f, j, z):
            s = 0.0
            s = self._add(s, f.index and f.index_up, 25)
            s = self._add(s, z, 55)
            s = self._pen(s, not z, 60)
            s = self._pen(s, f.middle or f.ring or f.pinky, 30)
            return s

        return {
            "A": score_A, "B": score_B, "C": score_C, "D": score_D, "E": score_E,
            "F": score_F, "G": score_G, "H": score_H, "I": score_I, "J": score_J,
            "K": score_K, "L": score_L, "M": score_M, "N": score_N, "O": score_O,
            "P": score_P, "Q": score_Q, "R": score_R, "S": score_S, "T": score_T,
            "U": score_U, "V": score_V, "W": score_W, "X": score_X, "Y": score_Y,
            "Z": score_Z,
        }

    def classify(self, finger_state: Optional[FingerState]) -> Optional[str]:
        if finger_state is None:
            self._reset_motion()
            return None

        j_motion, z_motion = self._update_motion(finger_state)

        scores: List[Tuple[str, float]] = []
        for letter, scorer in self._scorers.items():
            val = scorer(finger_state, j_motion, z_motion)
            if val > 0:
                scores.append((letter, val))

        if not scores:
            return None

        scores.sort(key=lambda x: x[1], reverse=True)
        best_letter, best_score = scores[0]
        second_score = scores[1][1] if len(scores) > 1 else 0.0

        if best_score < self.MIN_SCORE:
            return None
        if best_score - second_score < self.MIN_MARGIN and second_score > 0:
            return None

        return best_letter

    def classify_with_stability(self, finger_state: Optional[FingerState]) -> Optional[str]:
        letter = self.classify(finger_state)
        if letter is None:
            self._stability_count = 0
            self._last_letter = None
            return None
        if letter == self._last_letter:
            self._stability_count += 1
            if self._stability_count >= self._STABILITY_THRESHOLD:
                return letter
        else:
            self._last_letter = letter
            self._stability_count = 1
        return None

    def reset_stability(self) -> None:
        self._last_letter = None
        self._stability_count = 0
        self._reset_motion()
