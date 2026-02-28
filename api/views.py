"""
=============================================================
VISTAS — api/views.py
=============================================================
Las vistas reciben las peticiones HTTP de React,
procesan la lógica y retornan respuestas JSON.

Cada vista corresponde a un endpoint de la API.

Tipos de vistas usadas:
  - APIView: control manual sobre GET, POST, DELETE
  - generics.ListCreateAPIView: automático para listar y crear
  - @api_view: funciones simples para endpoints pequeños
=============================================================
"""

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from .models import Idea, Like, ReIdea, Comment, Follow, Profile
from .serializers import (
    IdeaSerializer, CommentSerializer,
    UserSerializer, RegisterSerializer
)


# ============================================================
# AUTENTICACIÓN
# ============================================================

class RegisterView(APIView):
    """
    POST /api/auth/register/
    Crea una nueva cuenta de usuario.
    
    Body esperado:
    {
        "username": "johndoe",
        "email": "john@example.com",
        "password": "mipassword123",
        "password2": "mipassword123",
        "first_name": "John",   (opcional)
        "last_name": "Doe"      (opcional)
    }
    """
    # permission_classes = cualquiera puede registrarse, sin token
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # Pasa los datos recibidos al serializer para validar
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            # Si los datos son válidos, crea el usuario
            user = serializer.save()

            # Genera tokens JWT para que el usuario quede autenticado inmediatamente
            refresh = RefreshToken.for_user(user)

            return Response({
                'message': '¡Cuenta creada exitosamente!',
                'user': UserSerializer(user, context={'request': request}).data,
                # El access token se usa en cada request
                'access': str(refresh.access_token),
                # El refresh token se usa para renovar el access token
                'refresh': str(refresh),
            }, status=status.HTTP_201_CREATED)

        # Si hay errores de validación, retorna los errores
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    POST /api/auth/login/
    Inicia sesión y retorna tokens JWT.
    
    Body esperado:
    {
        "username": "johndoe",
        "password": "mipassword123"
    }
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        # authenticate verifica username y contraseña (compara con el hash)
        user = authenticate(username=username, password=password)

        if user:
            # Credenciales correctas → genera tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user, context={'request': request}).data,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            })

        # Credenciales incorrectas
        return Response(
            {'error': 'Usuario o contraseña incorrectos.'},
            status=status.HTTP_401_UNAUTHORIZED
        )


class LogoutView(APIView):
    """
    POST /api/auth/logout/
    Invalida el refresh token (cierra sesión).
    
    Body esperado:
    {
        "refresh": "<refresh_token>"
    }
    """
    def post(self, request):
        try:
            # Obtiene el refresh token del body
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            # Blacklist = invalida el token para que no pueda usarse más
            token.blacklist()
            return Response({'message': 'Sesión cerrada correctamente.'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ============================================================
# IDEAS (publicaciones)
# ============================================================

class IdeaListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/ideas/      → Lista todas las ideas (paginadas, 20 por página)
    POST /api/ideas/      → Crea una nueva idea

    Hereda de ListCreateAPIView que automáticamente maneja:
      GET → retorna lista serializada
      POST → valida datos y crea objeto
    """
    serializer_class = IdeaSerializer

    def get_queryset(self):
        """
        Retorna las ideas a mostrar.
        Soporta filtrado por ?username=johndoe para ver ideas de un usuario.
        """
        queryset = Idea.objects.select_related('author', 'author__profile').all()

        # Filtro opcional: ?username=johndoe
        username = self.request.query_params.get('username')
        if username:
            queryset = queryset.filter(author__username=username)

        return queryset

    def perform_create(self, serializer):
        """
        Al crear una idea, automáticamente asigna el usuario autenticado como autor.
        El frontend no necesita enviar el author_id — se toma del token JWT.
        """
        serializer.save(author=self.request.user)

    def get_serializer_context(self):
        """
        Pasa el request al serializer para que pueda calcular is_liked, is_reideated, etc.
        """
        return {'request': self.request}


class IdeaDetailView(generics.RetrieveDestroyAPIView):
    """
    GET    /api/ideas/<id>/   → Ver una idea específica
    DELETE /api/ideas/<id>/   → Borrar una idea (solo el autor puede)
    """
    serializer_class = IdeaSerializer
    queryset = Idea.objects.all()

    def get_serializer_context(self):
        return {'request': self.request}

    def destroy(self, request, *args, **kwargs):
        """Solo el autor puede borrar su propia idea"""
        idea = self.get_object()
        if idea.author != request.user:
            return Response(
                {'error': 'No tienes permiso para borrar esta idea.'},
                status=status.HTTP_403_FORBIDDEN
            )
        idea.delete()
        return Response({'message': 'Idea eliminada.'}, status=status.HTTP_204_NO_CONTENT)


# ============================================================
# LIKES
# ============================================================

@api_view(['POST'])
def toggle_like(request, idea_id):
    """
    POST /api/ideas/<idea_id>/like/
    
    Si el usuario ya dio like → quita el like (toggle)
    Si el usuario no dio like → da like
    
    Este patrón "toggle" evita tener dos endpoints separados.
    """
    # get_object_or_404 retorna el objeto o lanza 404 si no existe
    idea = get_object_or_404(Idea, id=idea_id)

    # Busca si ya existe un like de este usuario en esta idea
    like, created = Like.objects.get_or_create(user=request.user, idea=idea)

    if not created:
        # Ya existía el like → lo elimina
        like.delete()
        return Response({
            'liked': False,
            'likes_count': idea.likes_count
        })

    # No existía → lo creó (get_or_create ya lo guardó)
    return Response({
        'liked': True,
        'likes_count': idea.likes_count
    })


# ============================================================
# REIDEAS (apoyo/amplificación)
# ============================================================

@api_view(['POST'])
def toggle_reidea(request, idea_id):
    """
    POST /api/ideas/<idea_id>/reidea/
    
    Igual que like, pero para el botón de "ReIdea".
    ReIdea = amplificar/apoyar una idea (como Retweet).
    """
    idea = get_object_or_404(Idea, id=idea_id)
    reidea, created = ReIdea.objects.get_or_create(user=request.user, idea=idea)

    if not created:
        reidea.delete()
        return Response({
            'reideated': False,
            'reideas_count': idea.reideas_count
        })

    return Response({
        'reideated': True,
        'reideas_count': idea.reideas_count
    })


# ============================================================
# COMENTARIOS
# ============================================================

class CommentListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/ideas/<idea_id>/comments/   → Lista comentarios de una idea
    POST /api/ideas/<idea_id>/comments/   → Agrega un comentario
    """
    serializer_class = CommentSerializer

    def get_queryset(self):
        """Filtra comentarios de la idea específica en la URL"""
        idea_id = self.kwargs['idea_id']
        return Comment.objects.filter(idea_id=idea_id).select_related('author', 'author__profile')

    def perform_create(self, serializer):
        """Asigna automáticamente el usuario y la idea al crear el comentario"""
        idea = get_object_or_404(Idea, id=self.kwargs['idea_id'])
        serializer.save(author=self.request.user, idea=idea)

    def get_serializer_context(self):
        return {'request': self.request}


# ============================================================
# FEED (ideas de usuarios seguidos)
# ============================================================

@api_view(['GET'])
def feed(request):
    """
    GET /api/feed/
    
    Retorna las ideas de los usuarios que sigue el usuario autenticado.
    Si no sigue a nadie, retorna las ideas más recientes de todos.
    """
    # Obtiene los IDs de los usuarios que sigue el usuario actual
    following_ids = Follow.objects.filter(
        follower=request.user
    ).values_list('following_id', flat=True)

    if following_ids:
        # Filtra ideas de esos usuarios
        ideas = Idea.objects.filter(author_id__in=following_ids).select_related(
            'author', 'author__profile'
        )
    else:
        # Si no sigue a nadie, muestra todas las ideas recientes
        ideas = Idea.objects.select_related('author', 'author__profile').all()[:20]

    serializer = IdeaSerializer(ideas, many=True, context={'request': request})
    return Response(serializer.data)


# ============================================================
# PERFILES DE USUARIO
# ============================================================

class UserProfileView(APIView):
    """
    GET /api/users/<username>/
    Retorna el perfil público de un usuario con sus estadísticas.
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        serializer = UserSerializer(user, context={'request': request})

        # Si hay usuario autenticado, incluye si lo sigue o no
        is_following = False
        if request.user.is_authenticated:
            is_following = Follow.objects.filter(
                follower=request.user,
                following=user
            ).exists()

        return Response({
            **serializer.data,
            'is_following': is_following
        })


# ============================================================
# FOLLOW / UNFOLLOW
# ============================================================

@api_view(['POST'])
def toggle_follow(request, username):
    """
    POST /api/users/<username>/follow/
    
    Si ya sigue al usuario → deja de seguirlo (unfollow)
    Si no lo sigue → lo sigue (follow)
    No puedes seguirte a ti mismo.
    """
    # No puedes seguirte a ti mismo
    if request.user.username == username:
        return Response(
            {'error': 'No puedes seguirte a ti mismo.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user_to_follow = get_object_or_404(User, username=username)

    follow, created = Follow.objects.get_or_create(
        follower=request.user,
        following=user_to_follow
    )

    if not created:
        # Ya lo seguía → dejar de seguir
        follow.delete()
        return Response({
            'following': False,
            'followers_count': user_to_follow.profile.followers_count
        })

    return Response({
        'following': True,
        'followers_count': user_to_follow.profile.followers_count
    })


# ============================================================
# PERFIL PROPIO (edición)
# ============================================================

class MyProfileView(APIView):
    """
    GET  /api/profile/   → Obtiene el perfil del usuario autenticado
    PUT  /api/profile/   → Actualiza bio, avatar, website, etc.
    """
    def get(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)

    def put(self, request):
        profile = request.user.profile

        # Actualiza campos del Profile
        bio = request.data.get('bio')
        website = request.data.get('website')
        avatar = request.FILES.get('avatar')  # request.FILES para archivos subidos

        if bio is not None:
            profile.bio = bio
        if website is not None:
            profile.website = website
        if avatar is not None:
            profile.avatar = avatar

        profile.save()

        # También permite actualizar nombre/apellido del User
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        if first_name is not None:
            request.user.first_name = first_name
        if last_name is not None:
            request.user.last_name = last_name
        request.user.save()

        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)
