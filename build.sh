#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Instalar dependencias de Python
echo "--- Instalando dependencias de Python (requirements.txt) ---"
pip install -r requirements.txt

# 2. Instalar dependencias de Node (vía django-tailwind)
#    (Esto instala Tailwind, Vite, React, etc. desde package.json)
echo "--- Instalando dependencias de Node (tailwind install) ---"
python manage.py tailwind install

# 3. Construir los estilos de Tailwind CSS
echo "--- Construyendo Tailwind CSS (tailwind build) ---"
python manage.py tailwind build

# 4. (¡NUEVO!) Construir los archivos de React (Vite)
#    (Esto ejecuta "vite build" desde package.json)
echo "--- Construyendo React (npm run build) ---"
npm run build

# 5. Recolectar archivos estáticos
#    (Esto recogerá el CSS de Tailwind y el JS de Vite)
echo "--- Recolectando archivos estáticos (collectstatic) ---"
python manage.py collectstatic --no-input

# 6. Aplicar migraciones
echo "--- Aplicando migraciones (migrate) ---"
python manage.py migrate

# 7. Crear Superusuario (tu script)
echo "--- Verificando superusuario ---"
python manage.py shell -c "
from django.contrib.auth import get_user_model
import os

User = get_user_model()
USERNAME = os.environ.get('DJANGO_SUPERUSER_USERNAME')
EMAIL = os.environ.get('DJANGO_SUPERUSER_EMAIL')
PASSWORD = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

if USERNAME and EMAIL and PASSWORD:
    if not User.objects.filter(username=USERNAME).exists():
        print(f'Creando superusuario {USERNAME}')
        User.objects.create_superuser(USERNAME, EMAIL, PASSWORD)
    else:
        print(f'Superusuario {USERNAME} ya existe.')
else:
    print('Variables de superusuario no configuradas, saltando creación.')
"