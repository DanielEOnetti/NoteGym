#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Instalar dependencias de Python
echo "--- Instalando dependencias de Python (requirements.txt) ---"
pip install -r requirements.txt

# --- Cambios aquí: Usar npm install en la raíz ---
# 2. Instalar dependencias de Node.js (en la raíz, donde está package.json)
echo "--- Instalando dependencias de Node (npm install) ---"
npm install 

# 3. Construir los archivos de React/Vite/Tailwind
#    Usamos 'npm run build' o 'npx vite build'. 
#    Si tu 'npm run build' llama a 'vite build', esto funcionará ahora que 'npm install'
#    se ejecutó en la raíz, asegurando que 'vite' esté disponible localmente.
echo "--- Construyendo Frontend (npm run build) ---"
npm run build 

# --- Fin de los cambios ---

# 4. Recolectar archivos estáticos
#    (Esto recogerá el CSS de Tailwind y el JS de Vite)
echo "--- Recolectando archivos estáticos (collectstatic) ---"
python manage.py collectstatic --no-input

# 5. Aplicar migraciones
echo "--- Aplicando migraciones (migrate) ---"
python manage.py migrate

# 6. Crear Superusuario (tu script)
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