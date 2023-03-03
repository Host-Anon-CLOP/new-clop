from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    first_name = None
    last_name = None

    email = models.EmailField(_("email address"), blank=True, null=True)
    register_ip = models.GenericIPAddressField("registration ip address", blank=True, null=True)

    REQUIRED_FIELDS = []

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    @property
    def has_nations(self):
        return self.nations.exists()

    @property
    def has_multiple_nations(self):
        return self.nations.count() > 1


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='profile')

    bio = models.TextField(max_length=1000, blank=True)
    flag = models.ImageField(upload_to='flags', blank=True, null=True)

    class COLOR_SCHEMES(models.TextChoices):
        LIGHT = 'light', _('Light')
        DARK = 'dark', _('Dark')
        SYSTEM = 'system', _('System')

    color_scheme = models.CharField(
        choices=COLOR_SCHEMES.choices,
        default=COLOR_SCHEMES.SYSTEM,
        max_length=50,
    )
    hide_banners = models.BooleanField(default=False)

    stasis = models.BooleanField(default=False)
    stasis_date = models.DateTimeField(blank=True, null=True)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
