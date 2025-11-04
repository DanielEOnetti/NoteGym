import os
from pathlib import Path
import environ  # Importado para gestionar variables de entorno

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Configuración de django-environ (CLAVE) ---
# https://django-environ.readthedocs.io/en/latest/
env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

# Lee el archivo .env si existe (para desarrollo local)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# --- Variables de Seguridad (Leídas desde el entorno) ---
# Render generará esto automáticamente
SECRET_KEY = env('SECRET_KEY')

# Render lo pondrá en False. Tu .env local debe tener DEBUG=True
DEBUG = env.bool('DEBUG')

# Render añadirá 'notegym.onrender.com' automáticamente.
# Añade tu dominio personalizado aquí si lo tienes.
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Render te da esta variable de entorno automáticamente
RENDER_EXTERNAL_HOSTNAME = env.str('RENDER_EXTERNAL_HOSTNAME', default=None)

# Si esa variable existe (es decir, estamos en Render)...
if RENDER_EXTERNAL_HOSTNAME:
    # ...la añadimos a la lista.
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'


# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",

    # --- Whitenoise (CLAVE CORREGIDA) ---
    # La *aplicación* va aquí
    "whitenoise", 
    "anymail",

    "django.contrib.staticfiles",
    "core",
    "tailwind",
    "theme",
    # "django_browser_reload", # Se añade condicionalmente más abajo
    'django.contrib.humanize',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # --- Whitenoise (CLAVE) ---
    # Debe ir justo después de SecurityMiddleware
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# --- Lógica condicional para DEBUG ---
# django_browser_reload solo debe correr en desarrollo
if DEBUG:
    INSTALLED_APPS.append("django_browser_reload")
    MIDDLEWARE.insert(
        MIDDLEWARE.index("django.middleware.security.SecurityMiddleware") + 1,
        "django_browser_reload.middleware.BrowserReloadMiddleware",
    )

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        'DIRS': [BASE_DIR / 'templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# --- Base de Datos (CLAVE) ---

# Por defecto, usamos SQLite para desarrollo local (si DEBUG=True)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Si NO estamos en DEBUG (es decir, en producción en Render)...
if not DEBUG:
    # ...entonces lee la DATABASE_URL que Render provee.
    DATABASES['default'] = env.db()


# Password validation
# ... (tu configuración está bien) ...
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# ... (tu configuración está bien) ...
LANGUAGE_CODE = "es"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# --- Archivos Estáticos (CSS, JavaScript, Images) (CLAVE) ---
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# --- ESTO SÍ ES CORRECTO ---
# El *motor de almacenamiento* va aquí
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]


# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# --- Configuración de Tailwind ---
TAILWIND_APP_NAME = 'theme'
INTERNAL_IPS = ["127.0.0.1"]

# ¡ELIMINADO! Esta ruta de Windows no funcionará en Render (Linux).
# El build.sh se encargará de instalar y correr npm.
# NPM_BIN_PATH = r"C:\Users\Melio\AppData\Roaming\npm\npm.cmd"


# --- Archivos Media (Subidos por usuarios) ---
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
# Advertencia: Render tiene un sistema de archivos efímero.
# Los archivos subidos a MEDIA_ROOT se borrarán en cada despliegue.
# La solución permanente es usar S3 (Opción 2).

if not DEBUG:
    # --- Configuración de Producción (Usa la API de Brevo) ---
    ANYMAIL = {
        # El backend de Brevo (usa la API, no SMTP)
        "SEND_DEFAULTS": {
            "ESP_EXTRA": {"sender": {"name": "Notegym"}},
        },
        "BREVO_API_KEY": env('ANYMAIL_BREVO_API_KEY'),
    }
    EMAIL_BACKEND = "anymail.backends.brevo.EmailBackend"
    DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL') # El email verificado de Brevo
else:
    # --- Configuración de Desarrollo (Usa la Consola) ---
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    DEFAULT_FROM_EMAIL = 'danieleonetti12@gmail.com'