# Imágenes de referencia — ASL

Imágenes del alfabeto manual de ASL (American Sign Language) que la app muestra
cuando el idioma de aprendizaje es **inglés**. ASL usa solo las 26 letras A-Z
(sin Ñ ni Ç).

Nombre de cada archivo: la letra en minúscula + `.png`, igual que en `../`.

## Origen de cada letra

Las letras cuya seña es equivalente en ASL se copian (imagen y muestras de
entrenamiento) desde LSC o Libras con `python build_asl_dataset.py`; el mapeo
está en `ASL_LETTER_SOURCES` de ese script.

| Origen | Letras |
|---|---|
| LSC (`../`) | B, C, G, H, I, J, K, O, V, W, X, Y, Z |
| Libras (`../libras/`) | A, D, E, L, P, R, S, U |
| Propia de ASL (pendiente) | F, M, N, Q, T |

J y Z se reconocen por su movimiento (`src/sign_language/motion_detector.py`).

## Pendiente

F, M, N, Q y T son distintas en LSC y en Libras, así que no tienen imagen ni
muestras todavía. Para completarlas:

1. Agregar `f.png`, `m.png`, `n.png`, `q.png` y `t.png` del alfabeto ASL en esta
   carpeta (mientras falten, la app muestra "Falta la imagen de la seña X").
2. Grabar 60 muestras por letra y reentrenar:
   `python collect_sign_samples.py --lang en --only F` (repetir con M, N, Q, T).

Las muestras grabadas de estas letras se conservan si se vuelve a ejecutar
`build_asl_dataset.py`. No grabes muestras de las letras reutilizadas con
`--lang en`, porque ese script las reemplaza con las de LSC o Libras.
