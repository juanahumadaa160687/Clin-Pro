from django.db import models

class NoRegistrado(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    apellido = models.CharField(max_length=100, verbose_name='Apellido')
    telefono = models.CharField(max_length=15, verbose_name='Teléfono')
    email = models.EmailField(verbose_name='Correo Electrónico', blank=True, null=True)

    def __str__(self):
        return f'{self.nombre} {self.apellido} - {self.telefono}'

    objects = models.Manager()

    class Meta:
        verbose_name = 'No Registrado'
        verbose_name_plural = 'No Registrados'