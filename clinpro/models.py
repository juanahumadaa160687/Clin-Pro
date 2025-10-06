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
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='User', blank=True, null=True)
    noregistrado = models.ForeignKey('recepcion.NoRegistrado', on_delete=models.CASCADE, verbose_name='No Registrado', blank=True, null=True)
    pago = models.ForeignKey(Pago, on_delete=models.CASCADE, verbose_name='Pago', blank=True, null=True)
    profesional = models.ForeignKey('administracion.PersonalSalud', on_delete=models.CASCADE, verbose_name='Profesional', blank=True, null=True)

    def __str__(self):
        return f"Reserva {self.fecha_reserva} de {self.hora_reserva}"

    objects = models.Manager()

    class Meta:
        verbose_name = 'Reserva de Hora'
        verbose_name_plural = 'Reservas de Horas'

########################################################################################################################