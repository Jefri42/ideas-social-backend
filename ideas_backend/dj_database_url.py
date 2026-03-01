import os
import dj_database_url

# 1. Configuración de Base de Datos "Híbrida"
DATABASES = {
    'default': dj_database_url.config(
        # Render usará la variable DATABASE_URL si existe.
        # Si no existe (en tu PC), usará tus datos de MySQL:
        default='mysql://root:Jefri2311.@127.0.0.1:3306/ideas_social',
        conn_max_age=600
    )
}

# 2. Configuración de Hosts permitidos
# El '.onrender.com' permite cualquier nombre de app que elijas en Render
ALLOWED_HOSTS = ['.onrender.com', 'localhost', '127.0.0.1']