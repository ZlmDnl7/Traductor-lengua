#!/bin/bash
# Script de instalacion - Enseñando
# Ejecutar desde la raiz del proyecto

set -e
echo "Creando entorno virtual (si no existe)..."
[ -d venv ] || python3 -m venv venv

echo "Activando venv e instalando dependencias..."
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Instalacion finalizada. Para ejecutar la aplicacion:"
echo "  source venv/bin/activate"
echo "  python run.py"
