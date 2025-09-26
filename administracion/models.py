from django.db import models
from kombu.abstract import Object


class PersonalSalud(models.Model):

    rut = models.CharField('RUT', max_length=255)
    nombre = models.CharField(max_length=255, verbose_name='Nombre')
    especialidad = models.CharField(max_length=100, verbose_name='Especialidad', default='Sin Especialidad')

    def __str__(self):
        return f'{self.nombre} - {self.especialidad}'

    objects = models.Manager()

    class Meta:
        verbose_name = 'Personal de Salud'
        verbose_name_plural = 'Personal de Salud'

class Servicio(models.Model):
    nombre = models.CharField(max_length=255, verbose_name='Nombre')

    personal = models.ManyToManyField(PersonalSalud, verbose_name='Profesional', blank=True, null=True)

    def __str__(self):
        return self.nombre

    objects = models.Manager()

    class Meta:
        verbose_name = 'Servicio'
        verbose_name_plural = 'Servicios'

class Procedimiento(models.Model):
    procedimiento = models.CharField(max_length=255, verbose_name='Procedimiento')
    precio = models.IntegerField(verbose_name='Precio', default=0)
    codigo = models.CharField(max_length=100, verbose_name='Código')
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
