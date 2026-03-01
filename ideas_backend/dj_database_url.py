import dj_database_url # Asegúrate de tener este import arriba

DATABASES = {
    'default': dj_database_url.config(
        # Esto se usará en tu PC (Localhost)
        default='mysql://root:Jefri2311.@localhost:3306/ideas_social',
        conn_max_age=600
    )
}

# Esto es necesario para MySQL en Django
DATABASES['default']['OPTIONS'] = {'charset': 'utf8mb4'}