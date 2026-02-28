"""
=============================================================
MODELOS — api/models.py
=============================================================
Los modelos son la representación de las tablas en MySQL.
Cada clase = una tabla en la base de datos.
Cada atributo = una columna en esa tabla.

Tablas que se crearán:
  - Profile       → Extiende el usuario con avatar, bio, etc.
  - Idea          → Las publicaciones (como tweets)
  - Like          → Registro de quién dio like a qué idea
  - ReIdea        → Registro de quién apoyó (reideó) qué idea
  - Comment       → Comentarios en las ideas
  - Follow        → Registro de quién sigue a quién
=============================================================
"""

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# ============================================================
# MODELO: Profile
# Extiende el User por defecto de Django con campos adicionales
# Relación: cada User tiene exactamente UN Profile (OneToOne)
# ============================================================
class Profile(models.Model):
    # OneToOneField = relación 1 a 1 con User
    # on_delete=CASCADE = si se borra el User, se borra el Profile también
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    # Foto de perfil — se guarda en /media/avatars/
    # blank=True, null=True = el campo es opcional
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    # Descripción del perfil (máximo 200 caracteres)
    bio = models.CharField(max_length=200, blank=True)

    # Sitio web personal (opcional)
    website = models.URLField(blank=True)

    # Fecha de nacimiento (opcional)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        # Cómo se muestra este objeto en el admin de Django
        return f'Perfil de @{self.user.username}'

    @property
    def followers_count(self):
        """Cuenta cuántas personas siguen a este usuario"""
        # Follow.objects.filter(following=self.user) busca en la tabla Follow
        # donde la columna 'following' sea este usuario
        return Follow.objects.filter(following=self.user).count()

    @property
    def following_count(self):
        """Cuenta a cuántas personas sigue este usuario"""
        return Follow.objects.filter(follower=self.user).count()

    @property
    def ideas_count(self):
        """Cuenta cuántas ideas ha publicado este usuario"""
        return Idea.objects.filter(author=self.user).count()


# ============================================================
# SEÑAL: Crea automáticamente un Profile cuando se crea un User
# Las señales son eventos — cuando pasa X, ejecuta Y
# post_save = después de guardar → sender=User = cuando el objeto es User
# ============================================================
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Se ejecuta automáticamente cada vez que se crea un nuevo User"""
    if created:
        # Solo crea el Profile si el User es nuevo (created=True)
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Guarda el Profile cuando se guarda el User"""
    instance.profile.save()


# ============================================================
# MODELO: Idea
# Las publicaciones de la red social (equivalente a Tweets)
# ============================================================
class Idea(models.Model):
    # ForeignKey = relación muchos a uno (un user puede tener muchas ideas)
    # related_name='ideas' → desde User puedes hacer user.ideas.all()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ideas')

    # El texto de la idea (máximo 280 caracteres, como Twitter)
    content = models.TextField(max_length=280)

    # Imagen opcional adjunta a la idea
    image = models.ImageField(upload_to='ideas/', blank=True, null=True)

    # auto_now_add=True = se pone automáticamente al crear
    created_at = models.DateTimeField(auto_now_add=True)

    # auto_now=True = se actualiza automáticamente cada vez que se guarda
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Ordenar las ideas de más reciente a más antigua por defecto
        ordering = ['-created_at']

    def __str__(self):
        return f'Idea de @{self.author.username}: {self.content[:50]}...'

    @property
    def likes_count(self):
        """Cuenta cuántos likes tiene esta idea"""
        return self.likes.count()

    @property
    def reideas_count(self):
        """Cuenta cuántos apoyos (reideas) tiene esta idea"""
        return self.reideas.count()

    @property
    def comments_count(self):
        """Cuenta cuántos comentarios tiene esta idea"""
        return self.comments.count()


# ============================================================
# MODELO: Like
# Registra quién dio like a qué idea
# Evita duplicados con unique_together
# ============================================================
class Like(models.Model):
    # El usuario que dio like
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')

    # La idea que recibió el like
    # related_name='likes' → desde Idea puedes hacer idea.likes.all()
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name='likes')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # unique_together = un usuario solo puede dar like una vez a cada idea
        # Si intenta dar like dos veces, MySQL lanzará un error
        unique_together = ('user', 'idea')

    def __str__(self):
        return f'@{self.user.username} ♥ Idea #{self.idea.id}'


# ============================================================
# MODELO: ReIdea
# El botón de "Reidea" significa dar soporte/amplificar una idea
# Funciona igual que Retweet en Twitter
# ============================================================
class ReIdea(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reideas')
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name='reideas')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Un usuario solo puede dar ReIdea una vez a cada idea
        unique_together = ('user', 'idea')

    def __str__(self):
        return f'@{self.user.username} ↻ Idea #{self.idea.id}'


# ============================================================
# MODELO: Comment
# Comentarios dentro de una idea
# ============================================================
class Comment(models.Model):
    # El usuario que comenta
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')

    # La idea en la que se comenta
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name='comments')

    # El texto del comentario
    content = models.TextField(max_length=500)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']  # Comentarios de más viejo a más nuevo

    def __str__(self):
        return f'@{self.author.username} comentó en Idea #{self.idea.id}'


# ============================================================
# MODELO: Follow
# Registra quién sigue a quién
# follower = el que sigue
# following = el que es seguido
# ============================================================
class Follow(models.Model):
    # El usuario que HACE el follow (el que presiona "Seguir")
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_set')

    # El usuario que RECIBE el follow (al que se sigue)
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers_set')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Un usuario no puede seguir dos veces al mismo usuario
        unique_together = ('follower', 'following')

    def __str__(self):
        return f'@{self.follower.username} → @{self.following.username}'
