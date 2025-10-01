from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver



class User(AbstractUser):
    email = models.EmailField(verbose_name='email', max_length=100, unique=True)
    password1 = models.CharField(verbose_name='password', max_length=128, null=True, blank=True)
    rut = models.CharField(verbose_name='RUT', max_length=128, null=True, blank=True)
    nombre = models.CharField(verbose_name='nombre', max_length=128, null=True, blank=True)
    telefono = models.CharField(verbose_name='telefono', max_length=128, null=True, blank=True)
    rol = models.CharField(verbose_name='rol', max_length=128, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.rut} {self.nombre}"

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

########################################################################################################################

class Paciente(models.Model):

    CHOICES = (
        ('Masculino', 'Masculino'),
        ('Femenino', 'Femenino'),
        ('Otro', 'Otro'),
        ('Prefiero no decirlo', 'Prefiero no decirlo'),
    )

    ISAPRE_CHOICES = (
        ('Fonasa', 'Fonasa'),
        ('Colmena', 'Colmena'),
        ('Consalud', 'Consalud'),
        ('Cruz Blanca', 'Cruz Blanca'),
        ('Vida Tres', 'Vida Tres'),
        ('Banmedica', 'Banmedica'),
        ('Otra', 'Otra'),
        ('Ninguna', 'Ninguna'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Usuario', null=True, blank=True)
    genero = models.CharField(verbose_name='Genero', max_length=128, null=True, blank=True)
    direccion = models.CharField(max_length=100, verbose_name='Direccion', blank=True, null=True)
    fecha_nacimiento = models.DateField(verbose_name='Fecha de Nacimiento', blank=True, null=True)
    telefono_emergencia = models.CharField(max_length=15, verbose_name='Teléfono de Emergencia', blank=True, null=True)
    prevision = models.CharField(max_length=100, verbose_name='Previsión', blank=True, null=True)

    def __str__(self):
        return f"{self.user.rut} {self.user.nombre}"

    objects = models.Manager()

    class Meta:
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'

@receiver(post_save, sender=User)
def create_paciente(sender, instance, created, **kwargs):
    if created:
        paciente = Paciente(user=instance)
        paciente.save()

post_save.connect(create_paciente, sender=User)

########################################################################################################################

class Convenio(models.Model):


    nombre = models.CharField(max_length=100, verbose_name='Nombre del Convenio', default='Sin Convenio')
    descuento = models.IntegerField(verbose_name='Descuento', default=0)

    def __str__(self):
        return f"Convenio: {self.nombre}"

    objects = models.Manager()

    class Meta:
        verbose_name = 'Convenio'
        verbose_name_plural = 'Convenios'

########################################################################################################################

class Pago(models.Model):

    orden_compra = models.CharField(max_length=50, verbose_name='Número de Compra', blank=True, null=True)
    fecha = models.DateField(verbose_name='Fecha del Pago')
    monto = models.DecimalField(max_digits=10, decimal_places=0, verbose_name='Monto del Pago')
    metodo_pago = models.CharField(max_length=50, verbose_name='Método de Pago', blank=True, null=True)
    is_pagado = models.BooleanField(default=False, verbose_name='¿Está Pagado?')

    convenio = models.ForeignKey(Convenio, on_delete=models.CASCADE, verbose_name='Convenio', blank=True, null=True)

    def __str__(self):
        return f"Pago nro {self.orden_compra} por {self.monto}"
    objects = models.Manager()

    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'

########################################################################################################################

class ReservaHora(models.Model):

    fecha_reserva = models.DateField(verbose_name='Fecha de la Reserva')
    hora_reserva = models.TimeField(verbose_name='Hora de Inicio')
    is_confirmada = models.BooleanField(default=False, verbose_name='¿Está Confirmada?')
    is_asistencia = models.BooleanField(default=False, verbose_name='¿Asistió?')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')

    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, verbose_name='Paciente')
    pago = models.ForeignKey(Pago, on_delete=models.CASCADE, verbose_name='Pago', blank=True, null=True)
    profesional = models.ForeignKey('administracion.PersonalSalud', on_delete=models.CASCADE, verbose_name='Profesional', blank=True, null=True)


    def __str__(self):
        return f"Reserva de {self.paciente.user.nombre} {self.fecha_reserva} de {self.hora_reserva}"

    objects = models.Manager()

    class Meta:
        verbose_name = 'Reserva de Hora'
        verbose_name_plural = 'Reservas de Horas'

########################################################################################################################