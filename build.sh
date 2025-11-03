#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Instalar dependencias de Python
pip install -r requirements.txt

# 2. Instalar dependencias de Node (¡LA FORMA CORRECTA!)
#    Esto ejecutará 'npm install' dentro de tu app 'theme/'
python manage.py tailwind install

# 3. Construir los estilos de Tailwind
python manage.py tailwind build

# 4. Recolectar archivos estáticos
python manage.py collectstatic --no-input

# 5. Aplicar migraciones
python manage.py migrate