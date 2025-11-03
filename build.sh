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

# 6. Crear Superusuario (¡NUEVO!)
# Esto usa las variables de entorno que pusiste en Render
python manage.py shell -c "
from django.contrib.auth import get_user_model
import os

User = get_user_model()
USERNAME = os.environ.get('DJANGO_SUPERUSER_USERNAME')
EMAIL = os.environ.get('DJANGO_SUPERUSER_EMAIL')
PASSWORD = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

if not User.objects.filter(username=USERNAME).exists():
    print(f'Creando superusuario {USERNAME}')
    User.objects.create_superuser(USERNAME, EMAIL, PASSWORD)
else:
    print(f'Superusuario {USERNAME} ya existe.')
"