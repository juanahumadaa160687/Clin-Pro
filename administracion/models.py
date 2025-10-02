from django.db import models
from django.db.models import CASCADE

from clinpro.models import User

class Secretaria(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'Secretaria: {self.user.nombre}'

    objects = models.Manager()

    class Meta:
        verbose_name = 'Secretaria'
        verbose_name_plural = 'Secretarias'

class Administrador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'Administrador: {self.user.nombre}'

    objects = models.Manager()

    class Meta:
        verbose_name = 'Administrador'
        verbose_name_plural = 'Administradores'

class PersonalSalud(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sufijo = models.CharField(max_length=4)
    titulo = models.CharField(max_length=100)
    especialidad = models.CharField(max_length=100, verbose_name='Especialidad', default='Sin Especialidad')
    universidad = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.sufijo} {self.user.nombre} - {self.titulo}'

    objects = models.Manager()

    class Meta:
        verbose_name = 'Personal de Salud'
        verbose_name_plural = 'Personal de Salud'

class Servicio(models.Model):
    nombre = models.CharField(max_length=255, verbose_name='Nombre')

    personal = models.ManyToManyField(PersonalSalud, verbose_name='Profesional', blank=True, null=True)
    recepcion = models.ManyToManyField(Secretaria, verbose_name='Recepcion', blank=True, null=True)
    administracion = models.ForeignKey(Administrador, on_delete=CASCADE, verbose_name='Administración', blank=True, null=True)

    def __str__(self):
        return self.nombre

    objects = models.Manager()

    class Meta:
        verbose_name = 'Servicio'
        verbose_name_plural = 'Servicios'

class Procedimiento(models.Model):
    procedimiento = models.CharField(max_length=255, verbose_name='Procedimiento')
    precio = models.IntegerField(verbose_name='Precio', default=0)

    personal_salud = models.ManyToManyField(PersonalSalud, verbose_name='Profesional', blank=True)

    def __str__(self):
        return self.procedimiento

    objects = models.Manager()

    class Meta:
        verbose_name = 'Procedimiento'
        verbose_name_plural = 'Procedimientos'

class Agenda(models.Model):
    fecha = models.DateField(verbose_name='Fecha')
    hora = models.TimeField(verbose_name='Hora')

    profesional = models.ForeignKey(PersonalSalud, on_delete=models.CASCADE, verbose_name='Profesional', blank=True, null=True)

    def __str__(self):
        return f"{self.fecha} - {self.hora} - {self.profesional}"

    objects = models.Manager()

    class Meta:
        verbose_name = 'Agenda'
        verbose_name_plural = 'Agendas'
