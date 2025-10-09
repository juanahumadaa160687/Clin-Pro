from django.db import models

class NoRegistrado(models.Model):
    rut = models.CharField(max_length=12, unique=True, verbose_name='RUT', blank=True, null=True)
    nombre = models.CharField(max_length=100, verbose_name='Nombre', blank=True, null=True)
    telefono = models.CharField(max_length=15, verbose_name='Teléfono', blank=True, null=True, default='No Presenta')
    email = models.EmailField(verbose_name='Correo Electrónico', blank=True, null=True, default='No Presenta', unique=True)
    rol = models.CharField(max_length=10, verbose_name='Rol', blank=True, null=True)

    def __str__(self):
        return f'{self.rut}- {self.nombre}'

    objects = models.Manager()

    class Meta:
        verbose_name = 'No Registrado'
        verbose_name_plural = 'No Registrados'