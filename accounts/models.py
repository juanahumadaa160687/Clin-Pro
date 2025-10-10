from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(verbose_name='email', max_length=100, unique=True)
    rut = models.CharField(verbose_name='RUT', max_length=128, null=True, blank=True)
    first_name = models.CharField(verbose_name='nombre', max_length=128, null=True, blank=True)
    last_name = models.CharField(verbose_name='apellido', max_length=128, null=True, blank=True)
    telefono = models.CharField(verbose_name='telefono', max_length=128, null=True, blank=True)
    rol = models.CharField(verbose_name='rol', max_length=128, null=True, blank=True)
    mfa_secret = models.CharField(verbose_name='mfa_secret', max_length=32, null=True, blank=True)
    mfa_verified = models.BooleanField(default=False, verbose_name='mfa_verified')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.rut} {self.first_name} {self.last_name}"

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'