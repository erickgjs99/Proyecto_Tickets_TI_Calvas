"""
models.py
---------
Modelos del sistema de gestión de tickets de soporte TI.

Incluye:
- UserProfile: Información extendida del usuario.
- Ticket: Modelo principal del sistema de soporte.
- Comment: Comentarios asociados a los tickets.

También incluye señales (signals) para crear automáticamente
perfiles de usuario al registrar un nuevo usuario.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


# =====================================================
# PERFIL DE USUARIO
# =====================================================
class UserProfile(models.Model):
    """
    Extiende el modelo de usuario de Django para incluir información adicional
    relevante para el entorno laboral, como cargo, departamento y datos de contacto.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    cargo = models.CharField(max_length=100, verbose_name='Cargo', blank=True)
    departamento = models.CharField(max_length=100, verbose_name='Departamento', blank=True)
    telefono = models.CharField(max_length=20, verbose_name='Teléfono', blank=True)
    extension = models.CharField(max_length=10, verbose_name='Extensión', blank=True)
    celular = models.CharField(max_length=10, verbose_name='Celular', blank=True)

    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'

    def __str__(self):
        """Muestra el nombre del usuario en representaciones de texto."""
        return f'Perfil de {self.user.username}'


# =====================================================
# SEÑALES DE CREACIÓN Y ACTUALIZACIÓN DE PERFILES
# =====================================================
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Crea un perfil automáticamente cada vez que se registra un nuevo usuario.
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Guarda el perfil asociado al usuario cada vez que el modelo User se actualiza.
    Si el usuario no tiene un perfil, se crea automáticamente.
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        UserProfile.objects.create(user=instance)


# =====================================================
# MODELO PRINCIPAL: TICKET
# =====================================================
class Ticket(models.Model):
    """
    Representa un ticket de soporte técnico creado por un usuario.

    Atributos:
        - ticket_number: Código único generado automáticamente (ej. TKT-00001)
        - user: Usuario que crea el ticket
        - title, description: Detalles del problema
        - category, priority, status: Clasificación y estado del ticket
        - assigned_to: Técnico o administrador asignado al ticket
        - created_at, updated_at: Fechas de creación y modificación
    """

    # Opciones de prioridad
    PRIORITY_CHOICES = [
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('critical', 'Crítica'),
    ]

    # Estados posibles del ticket
    STATUS_CHOICES = [
        ('open', 'Abierto'),
        ('in_progress', 'En Progreso'),
        ('resolved', 'Resuelto'),
        ('closed', 'Cerrado'),
    ]

    # Categorías de problemas frecuentes
    CATEGORY_CHOICES = [
        ('hardware', 'Hardware'),
        ('software', 'Software'),
        ('network', 'Red'),
        ('account', 'Cuenta'),
        ('other', 'Otro'),
    ]

    # Campos del modelo
    ticket_number = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        verbose_name='Número de Ticket'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tickets',
        verbose_name='Usuario'
    )
    title = models.CharField(max_length=200, verbose_name='Título')
    description = models.TextField(verbose_name='Descripción')
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='other',
        verbose_name='Categoría'
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name='Prioridad'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='open',
        verbose_name='Estado'
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets',
        verbose_name='Asignado a'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Creado el')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Actualizado el')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'

    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save() para generar un número de ticket único (TKT-00001, TKT-00002, ...).
        """
        if not self.ticket_number:
            last_ticket = Ticket.objects.order_by('-id').first()
            if last_ticket:
                last_number = int(last_ticket.ticket_number.split('-')[1])
                new_number = last_number + 1
            else:
                new_number = 1
            self.ticket_number = f'TKT-{new_number:05d}'
        super().save(*args, **kwargs)

    def __str__(self):
        """Representación legible del ticket."""
        return f'{self.ticket_number} - {self.title}'


# =====================================================
# COMENTARIOS DE TICKETS
# =====================================================
class Comment(models.Model):
    """
    Modelo que representa los comentarios agregados a un ticket por parte de usuarios o técnicos.
    """

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Ticket'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Usuario'
    )
    text = models.TextField(verbose_name='Comentario')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Creado el')

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'

    def __str__(self):
        """Devuelve una breve descripción del comentario."""
        return f'Comentario de {self.user.username} en {self.ticket.ticket_number}'
