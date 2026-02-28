#!/usr/bin/env python
"""
manage.py — Utilidad de línea de comandos de Django

Comandos más usados:
  python manage.py runserver          → Inicia el servidor
  python manage.py makemigrations     → Crea archivos de migración (cambios en modelos)
  python manage.py migrate            → Aplica migraciones a la base de datos
  python manage.py createsuperuser    → Crea un usuario administrador
  python manage.py shell              → Consola interactiva de Python con Django cargado
"""
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ideas_backend.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "No se pudo importar Django. ¿Activaste el entorno virtual?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
