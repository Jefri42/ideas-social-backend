"""
=============================================================
SERIALIZERS — api/serializers.py
=============================================================
Los serializers convierten los objetos de Python/Django
a formato JSON (para enviarlo al frontend) y viceversa
(para recibir datos del frontend y validarlos).

Piénsalo como un "traductor" entre tu base de datos y React.

Modelo Python → Serializer → JSON → React
React → JSON → Serializer (valida) → Modelo Python → MySQL
=============================================================
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Idea, Like, ReIdea, Comment, Follow


# ============================================================
# SERIALIZER: Profile
# Convierte el modelo Profile a JSON
# ============================================================
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        # Solo estos campos se incluirán en el JSON
        fields = ['avatar', 'bio', 'website', 'birth_date']


# ============================================================
# SERIALIZER: User (lectura)
# Para mostrar información de un usuario en el feed, comentarios, etc.
# ============================================================
class UserSerializer(serializers.ModelSerializer):
    # SerializerMethodField = campo calculado, no viene directo del modelo
    # Necesita un método get_<campo>() para calcular su valor
    avatar = serializers.SerializerMethodField()
    bio = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    ideas_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email',
                  'avatar', 'bio', 'followers_count', 'following_count', 'ideas_count']

    def get_avatar(self, obj):
        """Retorna la URL de la foto de perfil o None si no tiene"""
        request = self.context.get('request')
        if obj.profile.avatar and request:
            # build_absolute_uri convierte /media/avatars/foto.jpg
            # a http://localhost:8000/media/avatars/foto.jpg
            return request.build_absolute_uri(obj.profile.avatar.url)
        return None

    def get_bio(self, obj):
        return obj.profile.bio

    def get_followers_count(self, obj):
        return obj.profile.followers_count

    def get_following_count(self, obj):
        return obj.profile.following_count

    def get_ideas_count(self, obj):
        return obj.profile.ideas_count


# ============================================================
# SERIALIZER: Register (crear cuenta)
# Incluye validación de contraseña y campos especiales
# ============================================================
class RegisterSerializer(serializers.ModelSerializer):
    # write_only=True = solo se acepta en input, nunca se devuelve en respuesta
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)  # Confirmar contraseña

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password2']

    def validate(self, data):
        """Validación personalizada: verifica que ambas contraseñas coincidan"""
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password': 'Las contraseñas no coinciden.'})
        return data

    def validate_username(self, value):
        """Verifica que el username no esté en uso"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Este nombre de usuario ya está en uso.')
        return value

    def validate_email(self, value):
        """Verifica que el email no esté en uso"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Este email ya está registrado.')
        return value

    def create(self, validated_data):
        """Crea el usuario — usa create_user para hashear la contraseña"""
        # Quitar password2 antes de crear el usuario
        validated_data.pop('password2')

        # create_user hashea automáticamente la contraseña con bcrypt
        # NUNCA guardes contraseñas en texto plano
        user = User.objects.create_user(**validated_data)
        return user


# ============================================================
# SERIALIZER: Comment
# Para mostrar y crear comentarios
# ============================================================
class CommentSerializer(serializers.ModelSerializer):
    # Muestra el username del autor (solo lectura, se calcula automáticamente)
    author_username = serializers.CharField(source='author.username', read_only=True)
    author_avatar = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'author_username', 'author_avatar', 'content', 'created_at']
        # read_only_fields = estos campos se calculan solos, no se reciben del frontend
        read_only_fields = ['id', 'author_username', 'author_avatar', 'created_at']

    def get_author_avatar(self, obj):
        request = self.context.get('request')
        if obj.author.profile.avatar and request:
            return request.build_absolute_uri(obj.author.profile.avatar.url)
        return None


# ============================================================
# SERIALIZER: Idea
# La más compleja — incluye toda la información de una idea
# ============================================================
class IdeaSerializer(serializers.ModelSerializer):
    # Información del autor (usando UserSerializer anidado)
    author = UserSerializer(read_only=True)

    # Contadores
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    reideas_count = serializers.IntegerField(source='reideas.count', read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)

    # Flags: ¿el usuario actual ya dio like/reidea?
    # Estos se calculan en get_is_liked() y get_is_reideated()
    is_liked = serializers.SerializerMethodField()
    is_reideated = serializers.SerializerMethodField()

    class Meta:
        model = Idea
        fields = [
            'id', 'author', 'content', 'image',
            'likes_count', 'reideas_count', 'comments_count',
            'is_liked', 'is_reideated',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']

    def get_is_liked(self, obj):
        """Retorna True si el usuario actual ya dio like a esta idea"""
        request = self.context.get('request')
        # Si no hay usuario autenticado, retorna False
        if not request or not request.user.is_authenticated:
            return False
        # Busca si existe un Like con este usuario y esta idea
        return Like.objects.filter(user=request.user, idea=obj).exists()

    def get_is_reideated(self, obj):
        """Retorna True si el usuario actual ya dio ReIdea a esta idea"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return ReIdea.objects.filter(user=request.user, idea=obj).exists()
