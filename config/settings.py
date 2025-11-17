import os
from pathlib import Path
import environ 

# --- Configuración Inicial ---
BASE_DIR = Path(__file__).resolve().parent.parent

# Inicializa django-environ
env = environ.Env(
    # Define el valor por defecto para DEBUG
    DEBUG=(bool, False),
    # Define el valor por defecto para la DB: SQLite local. 
    # Si DATABASE_URL existe (en Render), se usará esa conexión.
    DATABASE_URL=(str, f'sqlite:///{BASE_DIR / "db.sqlite3"}') 
)

# Lee las variables del archivo .env (solo para desarrollo local)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('SECRET_KEY')
# DEBUG se lee desde tu archivo .env o usa el valor por defecto (False)
DEBUG = env.bool('DEBUG')

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Añade el hostname de Render si existe
RENDER_EXTERNAL_HOSTNAME = env.str('RENDER_EXTERNAL_HOSTNAME', default=None)
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# --- URLs de Autenticación ---
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'

# --- Aplicaciones ---
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "anymail",
    "django.contrib.staticfiles",
    'django.contrib.humanize',
    
    # Apps de Terceros
    'rest_framework',
    "tailwind",
    "theme",
    "django_vite",

    # Tus Apps
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Whitenoise debe estar aquí, justo después de SecurityMiddleware
    "whitenoise.middleware.WhiteNoiseMiddleware", 
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Añadir 'django_browser_reload' solo si estamos en DEBUG
if DEBUG:
    INSTALLED_APPS.append("django_browser_reload")
    # Insertar el middleware después de SecurityMiddleware para mejor compatibilidad
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

# --- Base de Datos (¡Configuración UNIFICADA y lista para Render!) ---
DATABASES = {
    # Lee la DB desde el entorno (PostgreSQL en Render o SQLite local)
    'default': env.db(),
}

# Configuración obligatoria de SSL para Render/PostgreSQL
# Esta sección se aplica solo si se está usando una conexión PostgreSQL
if 'OPTIONS' not in DATABASES['default']:
    DATABASES['default']['OPTIONS'] = {}
    
DATABASES['default']['OPTIONS']['sslmode'] = 'require'

# --- Configuración de Contraseñas ---
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- Internacionalización ---
LANGUAGE_CODE = "es"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --- Archivos Estáticos y Media ---
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --- Directorios de Estáticos Adicionales ---
# Necesario para django-vite/tailwind/archivos estáticos globales
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# --- Configuración de Tailwind ---
TAILWIND_APP_NAME = 'theme'
INTERNAL_IPS = ["127.0.0.1"]


# --- Configuración de Producción (if not DEBUG) ---
if not DEBUG:
    # --- Configuración de Email (Solo Producción) ---
    ANYMAIL = {
        "SEND_DEFAULTS": {
            "ESP_EXTRA": {"sender": {"name": "Notegym"}},
        },
        "BREVO_API_KEY": env('ANYMAIL_BREVO_API_KEY'),
    }
    EMAIL_BACKEND = "anymail.backends.brevo.EmailBackend"
    DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL') 
    
    # --- Configuración de Estáticos (Solo Producción) ---
    # Esto es el corazón de Whitenoise para producción
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

    # --- Configuración de Seguridad (Solo Producción) ---
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000  # 1 año
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

else:
    # --- Configuración de Email (Solo Desarrollo) ---
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    DEFAULT_FROM_EMAIL = 'danieleonetti12@gmail.com'


# --- DJANGO-VITE CONFIGURATION ---
DJANGO_VITE_DEV_MODE = DEBUG
DJANGO_VITE_DEV_SERVER_HOST = 'localhost'
DJANGO_VITE_DEV_SERVER_PORT = 5173
DJANGO_VITE_STATIC_URL_PREFIX = ''