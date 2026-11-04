#!/usr/bin/env python
# build_asl_dataset.py
# Arma el dataset, las imagenes y el modelo de ASL (American Sign Language)
# reutilizando las letras de LSC y LIBRAS cuya configuracion es equivalente en ASL.
#
# Solo LEE los datos de LSC (data/sign_language/) y LIBRAS (data/sign_language/libras/);
# nunca los modifica. Escribe en:
#   data/sign_language/asl/sign_samples.csv
#   data/sign_language/asl/sign_classifier.joblib
#   src/gui_web/web/assets/letras/asl/<letra>.png
#
# Las letras propias de ASL (ASL_OWN_LETTERS) no se copian: se graban con
#   python collect_sign_samples.py --lang en --only F
# Sus muestras se conservan si este script se vuelve a ejecutar.
#
#   python build_asl_dataset.py             # arma CSV + imagenes y entrena
#   python build_asl_dataset.py --no-train  # solo CSV + imagenes

from __future__ import annotations

import argparse
import csv
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.config import SIGN_ALPHABETS, SIGN_MODEL_FILES
from src.sign_language.sign_classifier import SignClassifier

_LETRAS_DIR = os.path.join(ROOT, "src", "gui_web", "web", "assets", "letras")

# Origen de cada letra de ASL. Solo se reutiliza cuando la configuracion de la mano
# (dedos, orientacion y movimiento) es equivalente a la de ASL. Si coincide con ambos
# alfabetos se elige el de mayor acierto en validacion cruzada; en empate, LSC.
#   (fuente, carpeta de imagenes)
_LSC = ("es", _LETRAS_DIR)
_LIBRAS = ("pt", os.path.join(_LETRAS_DIR, "libras"))
ASL_LETTER_SOURCES = {
    "A": _LIBRAS,  # puño con pulgar al costado (en LSC el pulgar va abierto)
    "B": _LSC,
    "C": _LSC,
    "D": _LIBRAS,
    "E": _LIBRAS,  # dedos doblados sobre el pulgar (en LSC el pulgar va abierto)
    "G": _LSC,     # indice y pulgar hacia el costado (LIBRAS: indice hacia arriba)
    "H": _LSC,     # indice y medio en horizontal (LIBRAS: V con giro)
    "I": _LSC,
    "J": _LSC,     # forma de I + gancho del menique (MotionDetector)
    "K": _LSC,     # estatica (LIBRAS agrega movimiento hacia arriba)
    "L": _LIBRAS,
    "O": _LSC,
    "P": _LIBRAS,  # K hacia abajo (LSC usa otra configuracion)
    "R": _LIBRAS,
    "S": _LIBRAS,  # puño con el pulgar cruzado por delante
    "U": _LIBRAS,  # indice y medio juntos (LSC: indice y menique)
    "V": _LSC,
    "W": _LSC,
    "X": _LSC,     # indice en gancho hacia arriba (LIBRAS: horizontal con movimiento)
    "Y": _LSC,
    "Z": _LSC,     # zigzag con el indice (MotionDetector)
}
# Distintas en LSC y en LIBRAS: necesitan muestras e imagenes propias de ASL.
ASL_OWN_LETTERS = tuple(L for L in SIGN_ALPHABETS["en"] if L not in ASL_LETTER_SOURCES)


def _read_rows(csv_path: str):
    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, [])
        rows = [row for row in reader if row]
    return header, rows


def build_csv() -> str:
    asl_csv, _ = SIGN_MODEL_FILES["en"]
    os.makedirs(os.path.dirname(asl_csv), exist_ok=True)

    header = None
    out_rows = []
    for lang in ("es", "pt"):
        src_csv, _ = SIGN_MODEL_FILES[lang]
        src_header, rows = _read_rows(src_csv)
        if header is None:
            header = src_header
        elif src_header != header:
            raise SystemExit(f"{src_csv} no tiene el mismo formato que el CSV de LSC.")
        wanted = {L for L, (src, _) in ASL_LETTER_SOURCES.items() if src == lang}
        out_rows += [row for row in rows if row[0].strip().upper() in wanted]

    # Muestras ya grabadas para las letras propias de ASL: no se pierden al reconstruir.
    if os.path.isfile(asl_csv):
        old_header, old_rows = _read_rows(asl_csv)
        if old_header == header:
            out_rows += [row for row in old_rows if row[0].strip().upper() in ASL_OWN_LETTERS]

    out_rows.sort(key=lambda row: SIGN_ALPHABETS["en"].index(row[0].strip().upper()))
    with open(asl_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(out_rows)
    return asl_csv


def copy_images() -> str:
    asl_dir = os.path.join(_LETRAS_DIR, "asl")
    os.makedirs(asl_dir, exist_ok=True)
    for letter, (_, folder) in ASL_LETTER_SOURCES.items():
        name = f"{letter.lower()}.png"
        shutil.copyfile(os.path.join(folder, name), os.path.join(asl_dir, name))
    return asl_dir


def main() -> None:
    p = argparse.ArgumentParser(description="Armar el dataset y el modelo de ASL a partir de LSC y LIBRAS.")
    p.add_argument("--no-train", action="store_true", help="Solo armar CSV e imagenes.")
    args = p.parse_args()

    asl_csv = build_csv()
    asl_dir = copy_images()
    clf = SignClassifier(language="en")
    counts = clf.count_samples_per_letter()
    print(f"CSV ASL: {asl_csv}")
    print(f"Imagenes ASL: {asl_dir}")
    print("Muestras por letra: " + " ".join(f"{L}:{n}" for L, n in counts.items()))
    pending = [L for L in ASL_OWN_LETTERS if counts.get(L, 0) == 0]
    if pending:
        print(
            "Pendientes (sin muestras ASL): " + ", ".join(pending)
            + "\n  Grabar con: python collect_sign_samples.py --lang en --only <LETRA>"
        )

    if args.no_train:
        return
    metrics = clf.train()
    path = clf.save_model()
    print(f"Modelo ASL: {path}  accuracy={metrics.get('accuracy', 0):.3f}  muestras={metrics.get('n_samples')}")


if __name__ == "__main__":
    main()
