"""
=============================================================
CONFIGURACIÓN PRINCIPAL DE DJANGO — ideas_backend/settings.py
=============================================================
Este archivo controla TODA la configuración del proyecto:
- Conexión a MySQL
- Apps instaladas
- Autenticación JWT
- CORS (para permitir que React se comunique con Django)
=============================================================
"""

from pathlib import Path
from datetime import timedelta
#import pymysql
#pymysql.install_as_MySQLdb()

# Directorio raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# ⚠️ SEGURIDAD: En producción, cambiar esta clave y ponerla en variables de entorno
#SECRET_KEY = 'django-insecure-ideas-social-change-this-in-production'
#SECRET_KEY = '^!17s)9nxpg9^@7*2@9vl)++t%!bs)-2s4vaewwha!%ueqt22*'
import os
SECRET_KEY = os.environ.get("c^vn=sm%h(%=*7qzvyirty=ijx&ond+cudzjitojnnl72w&g^h")

# ⚠️ En producción cambiar a False
DEBUG = True

# Hosts permitidos — en producción agregar tu dominio aquí
ALLOWED_HOSTS = ['localhost', '127.0.0.1']


# ============================================================
# APLICACIONES INSTALADAS
# Cada entrada es una "app" que Django carga al iniciar
# ============================================================
INSTALLED_APPS = [
    'django.contrib.admin',          # Panel de administración en /admin/
    'django.contrib.auth',           # Sistema de autenticación de Django
    'django.contrib.contenttypes',   # Tipos de contenido (necesario para permisos)
    'django.contrib.sessions',       # Manejo de sesiones
    'django.contrib.messages',       # Sistema de mensajes flash
    'django.contrib.staticfiles',    # Archivos estáticos (CSS, JS, imágenes del admin)

    # Apps de terceros
    'rest_framework',                # Django REST Framework — crea la API
    'rest_framework_simplejwt',      # JWT — sistema de tokens de autenticación
    'corsheaders',                   # CORS — permite que React hable con Django

    # Nuestra app principal
    'api',                           # Contiene modelos, vistas, serializers de Ideas
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',    # ← DEBE ir primero para que CORS funcione
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'ideas_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ideas_backend.wsgi.application'


# ============================================================
# BASE DE DATOS MYSQL
# Cambia los valores según tu configuración de MySQL
# ============================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ideas_social',   # ← nuevo nombre
        'USER': 'root',
        'PASSWORD': 'Jefri2311.',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

# ============================================================
# DJANGO REST FRAMEWORK — Configuración de la API
# ============================================================
REST_FRAMEWORK = {
    # Por defecto, todos los endpoints requieren autenticación JWT
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    # Endpoints de solo lectura son públicos, escritura requiere login
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    # Paginación: muestra 20 ideas por página
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}


# ============================================================
# JWT — Configuración de tokens de autenticación
# Los tokens funcionan así:
#   1. Usuario hace login → recibe access token (dura 1 hora) y refresh token (dura 7 días)
#   2. Cada request envía el access token en el header
#   3. Cuando expira, usa el refresh token para obtener uno nuevo
# ============================================================
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),   # Token de acceso dura 1 hora
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),   # Token de refresco dura 7 días
    'ROTATE_REFRESH_TOKENS': True,                  # Genera nuevo refresh token en cada uso
    'BLACKLIST_AFTER_ROTATION': True,               # Invalida el refresh token anterior
    'AUTH_HEADER_TYPES': ('Bearer',),               # Header: Authorization: Bearer <token>
}


# ============================================================
# CORS — Permite que React (puerto 3000) llame a Django (puerto 8000)
# Sin esto, el navegador bloquearía las peticiones por seguridad
# ============================================================
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',    # React en desarrollo
    'http://127.0.0.1:3000',
]

# Permite enviar cookies en requests cross-origin (necesario para refresh tokens)
CORS_ALLOW_CREDENTIALS = True


# ============================================================
# ARCHIVOS DE MEDIOS (fotos de perfil, imágenes en ideas)
# ============================================================
import os
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# Validaciones de contraseña
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
CORS_ALLOW_ALL_ORIGINS = True  # Solo para pruebas, luego lo cerramos