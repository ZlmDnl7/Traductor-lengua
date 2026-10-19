#!/usr/bin/env python
# collect_sign_samples.py
# Recoleccion interactiva de muestras (60 por letra) + entrenamiento del modelo.
# Con --lang pt se graba el alfabeto de LIBRAS y con --lang en el de ASL,
# cada uno en su propio dataset y modelo.
#
# Controles en la ventana:
#   ENTER  = empezar a grabar la letra / pasar a la siguiente letra
#   ESPACIO = pausar / reanudar mientras graba
#   R      = borrar todas las muestras de la letra actual y empezar de 0
#   Q      = salir (conserva lo ya tabla en el CSV)
#
# Ejemplos:
#   python collect_sign_samples.py
#   python collect_sign_samples.py --from B
#   python collect_sign_samples.py --only B --redo
#   python collect_sign_samples.py --lang pt
#   python collect_sign_samples.py --lang en --only F

from __future__ import annotations

import argparse
import os
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import cv2

from src.camera.camera_capture import CameraCapture
from src.config import CAMERA_INDEX, FRAME_HEIGHT, FRAME_WIDTH
from src.image_processing.hand_detector import HandDetector
from src.sign_language.sign_classifier import SignClassifier

_WAIT_START = "wait_start"
_COLLECTING = "collecting"
_PAUSED = "paused"
_LETTER_DONE = "letter_done"


def _draw_overlay(frame, lines: list[str], bar_current: int, bar_total: int, letter: str) -> None:
    h, w = frame.shape[:2]
    overlay = frame.copy()
    panel_h = min(h, 120 + 28 * len(lines))
    cv2.rectangle(overlay, (0, 0), (w, panel_h), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.55, frame, 0.45, 0, frame)

    y = 32
    for i, line in enumerate(lines):
        color = (0, 255, 255) if i == 0 else (240, 240, 240)
        scale = 0.95 if i == 0 else 0.65
        thick = 2 if i == 0 else 1
        cv2.putText(frame, line, (16, y), cv2.FONT_HERSHEY_SIMPLEX, scale, color, thick, cv2.LINE_AA)
        y += 34 if i == 0 else 26

    if bar_total > 0:
        bar_w = int(w * 0.72)
        bar_h = 26
        x0 = (w - bar_w) // 2
        y0 = h - 70
        cv2.rectangle(frame, (x0, y0), (x0 + bar_w, y0 + bar_h), (60, 60, 60), -1)
        fill = int(bar_w * (bar_current / max(bar_total, 1)))
        cv2.rectangle(frame, (x0, y0), (x0 + fill, y0 + bar_h), (0, 200, 80), -1)
        cv2.putText(
            frame,
            f"Letra {letter}: {bar_current}/{bar_total}",
            (x0, y0 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )


def _cv_label(letter: str) -> str:
    """Las fuentes de OpenCV solo dibujan ASCII: la Ç se muestra como texto."""
    return "C-cedilha" if letter == "Ç" else letter


def _status_lines(letter: str, collected: int, per_letter: int, phase: str) -> list[str]:
    if phase == _WAIT_START:
        if collected == 0:
            return [
                f"Letra {letter}",
                "Coloca la mano en la seña correcta.",
                "ENTER = empezar a grabar | R = borrar esta letra | Q = salir",
            ]
        return [
            f"Letra {letter} ({collected}/{per_letter} ya guardadas)",
            "ENTER = continuar grabando | R = borrar y empezar de 0 | Q = salir",
        ]
    if phase == _PAUSED:
        return [
            f"Letra {letter} — PAUSADO ({collected}/{per_letter})",
            "ESPACIO = reanudar | R = borrar letra | Q = salir",
        ]
    if phase == _LETTER_DONE:
        return [
            f"Letra {letter} completa ({per_letter}/{per_letter})",
            "Cambia la mano a la SIGUIENTE letra.",
            "ENTER = continuar | R = regrabar esta letra | Q = salir",
        ]
    return [
        f"Grabando letra {letter}...",
        "Mantén la seña estable. ESPACIO = pausar | R = borrar | Q = salir",
    ]


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Recolectar muestras de señas para entrenar el clasificador.")
    p.add_argument(
        "--lang",
        choices=("es", "en", "pt"),
        default="es",
        help="Alfabeto a grabar: es = LSC, pt = LIBRAS, en = ASL (cada uno con su modelo).",
    )
    p.add_argument(
        "--from",
        dest="start_letter",
        metavar="LETRA",
        help="Empezar en esta letra (ej: B). Las anteriores se conservan en el CSV.",
    )
    p.add_argument(
        "--only",
        dest="only_letter",
        metavar="LETRA",
        help="Recolectar solo una letra (ej: B).",
    )
    p.add_argument(
        "--redo",
        action="store_true",
        help="Borrar muestras existentes de la primera letra del lote antes de grabar.",
    )
    p.add_argument(
        "--no-train",
        action="store_true",
        help="No entrenar al final (solo recolectar).",
    )
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    clf = SignClassifier(language=args.lang)
    per_letter = clf.samples_per_letter

    try:
        from src.config import SIGN_SAMPLE_INTERVAL
        sample_interval = float(SIGN_SAMPLE_INTERVAL)
    except Exception:
        sample_interval = 0.25

    # La Ç (LIBRAS) tiene la misma forma estatica que la C: no se graba como clase
    # propia (confundiria al modelo); la app la detecta como C + movimiento.
    letters = [l for l in clf.letters if l != "Ç"]
    if args.only_letter:
        letters = [args.only_letter.upper()]
    elif args.start_letter:
        start = args.start_letter.upper()
        if start not in letters:
            print(f"Letra invalida: {start}")
            sys.exit(1)
        letters = letters[letters.index(start):]

    if args.redo and letters:
        removed = clf.remove_samples_for_letter(letters[0])
        print(f"Borradas {removed} muestras de la letra {letters[0]}.")

    alphabet_name = {"es": "LSC", "pt": "LIBRAS", "en": "ASL"}[args.lang]
    print(f"=== Recoleccion de muestras ({alphabet_name}) ===")
    print(f"CSV: {clf.samples_csv}")
    print(f"Muestras por letra: {per_letter}")
    print(f"Intervalo: {sample_interval}s entre muestras")
    print("ENTER = empezar / siguiente letra | ESPACIO = pausar | R = borrar letra | Q = salir")
    print()

    camera = CameraCapture(CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT)
    if not camera.open():
        print("No se pudo abrir la camara.")
        sys.exit(1)

    detector = HandDetector()
    window = "Recolectar senas"
    cv2.namedWindow(window, cv2.WINDOW_NORMAL)

    last_sample_ts = 0.0
    quit_requested = False

    try:
        for letter in letters:
            collected = clf.count_samples_for_letter(letter)
            phase = _WAIT_START if collected < per_letter else _LETTER_DONE
            last_sample_ts = 0.0

            if collected >= per_letter and not args.redo:
                print(f"  {letter}: ya tiene {collected} muestras (ENTER para pasar o R para regrabar).")

            while not quit_requested:
                ret, frame = camera.read()
                if not ret or frame is None:
                    continue

                ts = int(time.time() * 1000)
                landmarks, frame_out = detector.process(frame, timestamp_ms=ts)
                if landmarks is not None:
                    detector.draw_landmarks(frame_out, landmarks)

                lines = _status_lines(_cv_label(letter), collected, per_letter, phase)
                show_bar = phase in (_COLLECTING, _PAUSED, _LETTER_DONE)
                bar_n = collected if phase != _LETTER_DONE else per_letter
                _draw_overlay(frame_out, lines, bar_n, per_letter if show_bar else 0, _cv_label(letter))

                if phase == _COLLECTING and landmarks is not None:
                    now = time.monotonic()
                    if now - last_sample_ts >= sample_interval:
                        if clf.collect_sample(letter, landmarks):
                            collected += 1
                            last_sample_ts = now
                            if collected >= per_letter:
                                phase = _LETTER_DONE
                                print(f"  {letter}: {per_letter} muestras guardadas.")

                cv2.imshow(window, frame_out)
                key = cv2.waitKey(1) & 0xFF

                if key in (13, 10):  # Enter
                    if phase == _WAIT_START:
                        phase = _COLLECTING
                        last_sample_ts = 0.0
                    elif phase == _LETTER_DONE:
                        break
                elif key == ord(" "):
                    if phase == _COLLECTING:
                        phase = _PAUSED
                    elif phase == _PAUSED:
                        phase = _COLLECTING
                elif key == ord("r") or key == ord("R"):
                    removed = clf.remove_samples_for_letter(letter)
                    collected = 0
                    phase = _WAIT_START
                    last_sample_ts = 0.0
                    print(f"  {letter}: borradas {removed} muestras. Coloca la seña y pulsa ENTER.")
                elif key == ord("q") or key == ord("Q"):
                    quit_requested = True
                    print("Recoleccion detenida (datos ya guardados en CSV).")
                    break

            if quit_requested:
                break

        if quit_requested:
            return

        if args.no_train:
            print("\nRecoleccion terminada (sin entrenar). Ejecute: python train_sign_model.py")
            return

        print("\nRecoleccion completa. Entrenando modelo...")
        metrics = clf.train()
        path = clf.save_model()
        print(f"Entrenamiento listo. accuracy={metrics.get('accuracy', 0):.3f}")
        print(f"Modelo guardado en: {path}")
        print("Ya puede ejecutar: python run.py")

    finally:
        camera.release()
        detector.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
