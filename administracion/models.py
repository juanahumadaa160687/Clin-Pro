from django.db import models
from django.db.models import CASCADE
from clinpro.models import User

class PersonalSalud(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    prefijo = models.CharField(max_length=7, verbose_name='Sufijo', default='Sr(a).', blank=True, null=True)
    titulo = models.CharField(max_length=100)
    especialidad = models.CharField(max_length=100, verbose_name='Especialidad', default='Sin Especialidad')
    universidad = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.prefijo} {self.user.nombre} - {self.titulo} - {self.especialidad}'

    objects = models.Manager()

    class Meta:
        verbose_name = 'Personal de Salud'
        verbose_name_plural = 'Personal de Salud'

class Servicio(models.Model):
    nombre = models.CharField(max_length=255, verbose_name='Nombre')

    personal = models.ManyToManyField(PersonalSalud, verbose_name='Profesional')

    def __str__(self):
        return f'Servicio: {self.nombre}'

    objects = models.Manager()

    class Meta:
        verbose_name = 'Servicio'
        verbose_name_plural = 'Servicios'

class Procedimiento(models.Model):
    procedimiento = models.CharField(max_length=255, verbose_name='Procedimiento')
    precio = models.IntegerField(verbose_name='Precio', default=0)

    personal_salud = models.ManyToManyField(PersonalSalud, verbose_name='Profesional')

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
