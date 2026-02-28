import dj_database_url
import os

DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3', # Fallback for local dev
        conn_max_age=600
    )
}

ALLOWED_HOSTS = ['your-app-name.onrender.com', 'localhost', '127.0.0.1']