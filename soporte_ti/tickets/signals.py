from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def manage_user_profile(sender, instance, created, **kwargs):
    if created:
        # Crea el perfil SÓLO si el usuario es nuevo
        UserProfile.objects.create(user=instance)
    else:
        # Si el usuario ya existe (es una actualización), guarda su perfil
        try:
            instance.profile.save()
        except UserProfile.DoesNotExist:
            # Si el usuario ya existe pero por alguna razón no tiene perfil, lo crea
            UserProfile.objects.create(user=instance)