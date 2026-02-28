"""
=============================================================
URLs DE LA API — api/urls.py
=============================================================
Aquí conectamos cada URL con su vista correspondiente.

Todas estas URLs tienen el prefijo /api/ (definido en ideas_backend/urls.py)
Ejemplo: /api/ideas/ → IdeaListCreateView
=============================================================
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [

    # ----------------------------------------------------------
    # AUTENTICACIÓN
    # ----------------------------------------------------------

    # Registrar nueva cuenta
    path('auth/register/', views.RegisterView.as_view(), name='register'),

    # Login → retorna access + refresh token
    path('auth/login/', views.LoginView.as_view(), name='login'),

    # Logout → invalida el refresh token
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),

    # Renovar access token con el refresh token
    # Esta vista viene incluida en simplejwt, no necesitamos crearla
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),


    # ----------------------------------------------------------
    # IDEAS
    # GET /api/ideas/          → Listar todas las ideas
    # POST /api/ideas/         → Crear idea
    # GET /api/ideas/<id>/     → Ver idea específica
    # DELETE /api/ideas/<id>/  → Eliminar idea
    # ----------------------------------------------------------
    path('ideas/', views.IdeaListCreateView.as_view(), name='idea-list'),
    path('ideas/<int:pk>/', views.IdeaDetailView.as_view(), name='idea-detail'),

    # ----------------------------------------------------------
    # INTERACCIONES
    # POST /api/ideas/<id>/like/    → Toggle like
    # POST /api/ideas/<id>/reidea/  → Toggle reidea
    # ----------------------------------------------------------
    path('ideas/<int:idea_id>/like/', views.toggle_like, name='toggle-like'),
    path('ideas/<int:idea_id>/reidea/', views.toggle_reidea, name='toggle-reidea'),

    # ----------------------------------------------------------
    # COMENTARIOS
    # GET  /api/ideas/<id>/comments/  → Ver comentarios
    # POST /api/ideas/<id>/comments/  → Agregar comentario
    # ----------------------------------------------------------
    path('ideas/<int:idea_id>/comments/', views.CommentListCreateView.as_view(), name='comments'),

    # ----------------------------------------------------------
    # FEED
    # GET /api/feed/  → Ideas de usuarios seguidos
    # ----------------------------------------------------------
    path('feed/', views.feed, name='feed'),

    # ----------------------------------------------------------
    # PERFILES
    # GET /api/users/<username>/          → Ver perfil público
    # POST /api/users/<username>/follow/  → Seguir / dejar de seguir
    # ----------------------------------------------------------
    path('users/<str:username>/', views.UserProfileView.as_view(), name='user-profile'),
    path('users/<str:username>/follow/', views.toggle_follow, name='toggle-follow'),

    # ----------------------------------------------------------
    # MI PERFIL (usuario autenticado)
    # GET /api/profile/  → Ver mi perfil
    # PUT /api/profile/  → Editar mi perfil
    # ----------------------------------------------------------
    path('profile/', views.MyProfileView.as_view(), name='my-profile'),
]
