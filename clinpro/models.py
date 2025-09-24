from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver



class User(AbstractUser):
    email = models.EmailField(verbose_name='email address', max_length=100, unique=True)
    password1 = models.CharField(verbose_name='password', max_length=128, null=True, blank=True)
    is_staff = models.BooleanField(blank=True, default=False)
    is_active = models.BooleanField(blank=True, default=True)
    is_superuser = models.BooleanField(blank=True, default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

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

class Paciente(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Usuario', null=True, blank=True)
    rut = models.CharField(max_length=15, verbose_name='RUT del Paciente')
    nombre = models.CharField(max_length=100, verbose_name='Nombre', blank=True, null=True)
    apellido = models.CharField(max_length=100, verbose_name='Apellido', blank=True, null=True)
    direccion = models.CharField(max_length=100, verbose_name='Direccion', blank=True, null=True)
    telefono = models.CharField(max_length=15, verbose_name='Telefono', blank=True, null=True)
    prevision = models.CharField(max_length=100, verbose_name='Previsión', blank=True, null=True)

    convenios = models.ManyToManyField(Convenio, verbose_name='Convenios')

    def __str__(self):
        return f"{self.nombre} - {self.apellido} - {self.rut}"

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

class Pago(models.Model):

    orden_compra = models.CharField(max_length=50, verbose_name='Número de Orden de Compra', blank=True, null=True)
    fecha = models.DateField(verbose_name='Fecha del Pago')
    monto = models.DecimalField(max_digits=10, decimal_places=0, verbose_name='Monto del Pago')
    metodo_pago = models.CharField(max_length=50, verbose_name='Método de Pago', blank=True, null=True)
    is_pagado = models.BooleanField(default=False, verbose_name='¿Está Pagado?')

    def __str__(self):
        return f"Pago nro {self.orden_compra} por {self.monto}"
    objects = models.Manager()

    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'

########################################################################################################################

class ReservaHora(models.Model):

    fecha = models.DateField(verbose_name='Fecha de la Reserva')
    hora_inicio = models.TimeField(verbose_name='Hora de Inicio')
    hora_fin = models.TimeField(verbose_name='Hora de Fin')
    is_confirmada = models.BooleanField(default=False, verbose_name='¿Está Confirmada?')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')

    paciente_id = models.ForeignKey(Paciente, on_delete=models.CASCADE, verbose_name='Paciente')
    pago_id = models.ForeignKey(Pago, on_delete=models.CASCADE, verbose_name='Pago', blank=True, null=True)

    def __str__(self):
        return f"Reserva para {self.fecha} de {self.hora_inicio} a {self.hora_fin}"

    objects = models.Manager()

    class Meta:
        verbose_name = 'Reserva de Hora'
        verbose_name_plural = 'Reservas de Horas'

########################################################################################################################