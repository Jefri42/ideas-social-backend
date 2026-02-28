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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Panel de administración — solo para el superusuario
    path('admin/', admin.site.urls),

    # Toda la API — redirige a api/urls.py para el detalle
    # Ejemplo: /api/ideas/ → definido en api/urls.py
    path('api/', include('api.urls')),
]

# En desarrollo, Django sirve los archivos de media (fotos de perfil, etc.)
# En producción, esto lo maneja Nginx o un CDN
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
