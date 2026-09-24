"""
=============================================================
URLS PRINCIPALES — ideas_backend/urls.py
=============================================================
Este archivo es el "router" principal de Django.
Aquí definimos qué URL lleva a qué parte del código.

Estructura de URLs:
  /admin/          → Panel de administración de Django
  /api/            → Toda nuestra API REST (definida en api/urls.py)
  /media/          → Archivos subidos por usuarios (fotos, etc.)
=============================================================
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    # Panel de administración — solo para el superusuario
    path('admin/', admin.site.urls),

    # Toda la API — redirige a api/urls.py para el detalle
    # Ejemplo: /api/ideas/ → definido en api/urls.py
    path('api/', include('api.urls')),
]

# Archivos subidos por los usuarios (avatares, imágenes de ideas).
#
# Antes esto colgaba de `if settings.DEBUG:`, y el helper `static()` devuelve
# una lista vacía cuando DEBUG es False. Es decir: el /media/ de producción
# solo funcionaba porque el servidor estaba corriendo en modo debug. Al
# apagar DEBUG, cada avatar daba 404.
#
# WhiteNoise sirve STATIC_ROOT, pero no MEDIA_ROOT, así que la ruta se
# declara explícitamente y ya no depende de DEBUG.
urlpatterns += [
    re_path(
        r"^media/(?P<path>.*)$",
        serve,
        {"document_root": settings.MEDIA_ROOT},
    ),
]
