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

    personal = models.ManyToManyField(PersonalSalud, verbose_name='Profesional', blank=True, null=True)
    recepcion = models.ManyToManyField(Secretaria, verbose_name='Recepcion', blank=True, null=True)
    administracion = models.ForeignKey(Administrador, on_delete=CASCADE, verbose_name='Administración', blank=True, null=True)

    def __str__(self):
        return f'Administrado por: {self.administracion.user.nombre} - Servicio: {self.nombre}'

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

class PacienteNoRegistrado(models.Model):
    rut = models.CharField(max_length=12, verbose_name='RUT', unique=True)
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    genero = models.CharField(max_length=100, verbose_name='Genero')
    edad = models.IntegerField(verbose_name='Edad', blank=True, null=True),
    email = models.EmailField(verbose_name='Email', unique=True, blank=True, null=True)
    telefono = models.CharField(max_length=15, verbose_name='Teléfono', blank=True, null=True)
    direccion = models.CharField(max_length=255, verbose_name='Dirección', blank=True, null=True)
    fecha_nacimiento = models.DateField(verbose_name='Fecha de Nacimiento', blank=True, null=True)
    prevision = models.CharField(max_length=100, verbose_name='Previsión', blank=True, null=True)
    telefono_emergencia = models.CharField(max_length=15, verbose_name='Teléfono de Emergencia', blank=True, null=True)


    def __str__(self):
        return f'Paciente No Registrado: {self.nombre}'

    objects = models.Manager()

    class Meta:
        verbose_name = 'Paciente No Registrado'
        verbose_name_plural = 'Pacientes No Registrados'