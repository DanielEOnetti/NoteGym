#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Construir los estilos de Tailwind
python manage.py tailwind build

# 3. Recolectar archivos estáticos (para Whitenoise)
python manage.py collectstatic --no-input

# 4. Aplicar migraciones de la base de datos
python manage.py migrate