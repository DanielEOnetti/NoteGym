import os
from pathlib import Path
import environ  


BASE_DIR = Path(__file__).resolve().parent.parent


env = environ.Env(
    DEBUG=(bool, False)
)


environ.Env.read_env(os.path.join(BASE_DIR, '.env'))


SECRET_KEY = env('SECRET_KEY')


DEBUG = env.bool('DEBUG')


ALLOWED_HOSTS = ['localhost', '127.0.0.1']


RENDER_EXTERNAL_HOSTNAME = env.str('RENDER_EXTERNAL_HOSTNAME', default=None)


if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'



INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "anymail",
    "django.contrib.staticfiles",
    "django_vite",
    "core",
    "tailwind",
    "theme",
    'django.contrib.humanize',
    'rest_framework',
    
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


if not DEBUG:
    DATABASES['default'] = env.db()



AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]



LANGUAGE_CODE = "es"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True



STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"


STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# --- Configuración de Tailwind ---
TAILWIND_APP_NAME = 'theme'
INTERNAL_IPS = ["127.0.0.1"]
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


if not DEBUG:
    ANYMAIL = {
        "SEND_DEFAULTS": {
            "ESP_EXTRA": {"sender": {"name": "Notegym"}},
        },
        "BREVO_API_KEY": env('ANYMAIL_BREVO_API_KEY'),
    }
    EMAIL_BACKEND = "anymail.backends.brevo.EmailBackend"
    DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL') 
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    DEFAULT_FROM_EMAIL = 'danieleonetti12@gmail.com'

if not DEBUG:
   
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000  # 1 año
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True



# --- CONFIGURACIÓN DE DJANGO-VITE ---

# 1. El puerto del servidor de desarrollo de Vite (debe coincidir con vite.config.js)
DJANGO_VITE_DEV_SERVER_PORT = 5173

# 2. Dónde buscar el 'manifest.json' (debe coincidir con 'outDir' en vite.config.js)
DJANGO_VITE_MANIFEST_PATH = BASE_DIR / 'static' / 'dist' / 'manifest.json'

# 3. (Opcional pero recomendado) Nombre del Manifest
DJANGO_VITE_MANIFEST_FILENAME = 'manifest.json'

# 4. (Opcional) Dónde están los archivos estáticos de Vite
DJANGO_VITE_ASSETS_PATH = BASE_DIR / 'static' / 'dist'

# 5. (Importante) Incluir los archivos de Vite en tus estáticos
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
    DJANGO_VITE_ASSETS_PATH, # <-- AÑADE ESTA LÍNEA
]