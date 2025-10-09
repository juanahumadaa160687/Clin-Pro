from django.db import models
from accounts.models import User


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