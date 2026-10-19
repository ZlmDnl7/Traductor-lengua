#!/usr/bin/env python
# train_sign_model.py — Reentrena el modelo desde sign_samples.csv (sin recolectar).
#
#   python train_sign_model.py            # LSC (alfabeto original)
#   python train_sign_model.py --lang pt  # LIBRAS
#   python train_sign_model.py --lang en  # ASL

import argparse
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.sign_language.sign_classifier import SignClassifier


def main() -> None:
    p = argparse.ArgumentParser(description="Reentrenar el clasificador de señas.")
    p.add_argument("--lang", choices=("es", "en", "pt"), default="es", help="es = LSC, pt = LIBRAS, en = ASL")
    args = p.parse_args()

    clf = SignClassifier(language=args.lang)
    print(f"CSV: {clf.samples_csv}")
    metrics = clf.train()
    path = clf.save_model()
    print(f"Listo. accuracy={metrics.get('accuracy', 0):.3f}  muestras={metrics.get('n_samples')}")
    print(f"Modelo: {path}")


if __name__ == "__main__":
    main()
