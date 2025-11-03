Django expert
Gem personalizado
¡Perfecto! El Paso 1 es el más crítico para la seguridad. Vamos a "blindar" tu settings.py.

El objetivo es nunca escribir información sensible (como tu SECRET_KEY o contraseñas) directamente en el código. Usaremos variables de entorno para esto. La mejor librería para gestionar esto en Django es django-environ.

🚀 Paso 1: Configurar settings.py con django-environ
1.1. Instalar la librería
Abre tu terminal (con tu entorno virtual activado) e instala django-environ:

Bash
pip install django-environ
(No olvides añadirlo a tu requirements.txt: pip freeze > requirements.txt)

1.2. Crear tu archivo .env
En la raíz de tu proyecto (al mismo nivel que manage.py), crea un nuevo archivo llamado .env (literalmente, solo .env).

Este archivo guardará todos tus secretos. Nunca debe subirse a Git.

Escribe lo siguiente en tu archivo .env:

Ini, TOML
# Este es tu archivo .env
# Configuración de Seguridad
DEBUG=False
SECRET_KEY='tu-clave-secreta-de-django-muy-larga-y-complicada'
ALLOWED_HOSTS='localhost, 127.0.0.1, .mi-notegym.com'

# Configuración de Base de Datos (Nos adelantamos al Paso 3)
DATABASE_URL='sqlite:///' # De momento usamos SQLite
# DATABASE_URL='postgres://USER:PASS@HOST:PORT/DBNAME' # Así se verá en producción

# Configuración de Email (Nos adelantamos al Paso 2)
EMAIL_HOST='smtp.sendgrid.net'
EMAIL_PORT=587
EMAIL_HOST_USER='apikey'
EMAIL_HOST_PASSWORD='TU_API_KEY_DE_SENDGRID_IRA_AQUI'
DEFAULT_FROM_EMAIL='NoteGym <no-reply@mi-notegym.com>'
Acción Crítica: Ahora, abre tu archivo .gitignore y añade .env al final.

Fragmento de código
# .gitignore
*.pyc
__pycache__/
db.sqlite3
.env  <-- AÑADE ESTA LÍNA
Esto previene que accidentalmente subas tus contraseñas a tu repositorio de Git.

1.3. Modificar tu settings.py
Ahora, vamos a hacer que settings.py lea los valores de ese archivo .env.

Al principio de tu settings.py, importa environ y configúralo:

Python
# settings.py

import environ  # <-- Importar
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Configuración de django-environ ---
env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

# Lee el archivo .env
environ.Env.read_env(BASE_DIR / '.env')
# ------------------------------------
Ahora, busca las variables originales de Django (SECRET_KEY, DEBUG, ALLOWED_HOSTS) y reemplázalas por esto:

Python
# settings.py

# ... (después del código anterior)

# CLAVE SECRETA
# Lee la variable 'SECRET_KEY' de tu archivo .env
# Django fallará si esta variable no existe.
SECRET_KEY = env('SECRET_KEY')

# DEBUG
# Lee 'DEBUG', la convierte a Booleano (True/False), y si no la encuentra, usa False.
DEBUG = env.bool('DEBUG', default=False)
# O simplemente:
# DEBUG = env('DEBUG', cast=bool)


# HOSTS PERMITIDOS
# Lee 'ALLOWED_HOSTS' y la convierte en una lista de Python.
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')


# ... (sigue tu configuración de APPS, MIDDLEWARE, etc.)
1.4. (Opcional) Configurar la Base de Datos y Email
Ya que estamos aquí, puedes aprovechar y configurar también la base de datos y el email para que lean del .env.

Para la Base de Datos:

Busca tu sección DATABASES y reemplázala:

Python
# settings.py

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# Lee la variable 'DATABASE_URL' del .env y la configura.
DATABASES = {
    'default': env.db(),
}
Nota: env.db() buscará automáticamente la variable DATABASE_URL. Si no la encuentra, buscará SQLITE_URL. Por eso nuestro .env con DATABASE_URL='sqlite:///' funcionará en desarrollo, y cuando pongas la URL de PostgreSQL para producción, la tomará automáticamente.

Para el Email (Tu duda del Paso 2):

Busca (o añade) las variables de Email y configúralas para que lean del .env:

Python
# settings.py

# Email Settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='smtp.sendgrid.net')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='apikey')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='webmaster@localhost')
🏁 ¡Listo el Paso 1!
Has logrado lo siguiente:

Tu settings.py ya no contiene secretos. Es seguro subirlo a Git.

Tu DEBUG está automáticamente en False, protegiéndote en producción.

Tu ALLOWED_HOSTS está listo para ser configurado.

Tu archivo .env local te permite seguir desarrollando con DEBUG=True (simplemente cámbialo en el archivo) sin afectar la configuración de producción.

Has preparado el terreno para configurar el email y la base de datos de producción.