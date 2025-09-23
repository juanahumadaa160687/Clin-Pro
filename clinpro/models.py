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



class Paciente(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Usuario', null=True, blank=True)
    rut = models.CharField(max_length=15, verbose_name='RUT del Paciente')
    nombre = models.CharField(max_length=100, verbose_name='Nombre', blank=True, null=True)
    apellido = models.CharField(max_length=100, verbose_name='Apellido', blank=True, null=True)
    direccion = models.CharField(max_length=100, verbose_name='Direccion', blank=True, null=True)
    telefono = models.CharField(max_length=15, verbose_name='Telefono', blank=True, null=True)
    prevision = models.CharField(max_length=100, verbose_name='Previsión', blank=True, null=True)

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



class Profesional(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Usuario', null=True, blank=True)
    rut = models.CharField(max_length=12, unique=True, verbose_name='Rut', blank=True, null=True)
    nombre = models.CharField(max_length=100, verbose_name='Nombre', blank=True, null=True)
    apellido = models.CharField(max_length=100, verbose_name='Apellido', blank=True, null=True)
    telefono = models.CharField(max_length=15, unique=True, verbose_name='Telefono', blank=True, null=True)
    servicio = models.CharField(max_length=100, verbose_name='Servicio', blank=True, null=True)
    especialidad = models.CharField(max_length=100, verbose_name='Especialidad', blank=True, null=True, default='Sin Especialidad')

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    objects = models.Manager()

    class Meta:
        verbose_name = 'Profesional'
        verbose_name_plural = 'Profesionales'



class Prestacion(models.Model):

    nombre = models.CharField(max_length=100, verbose_name='Nombre de la Prestación')
    codigo = models.CharField(max_length=20, verbose_name='Código', unique=True)
    precio = models.DecimalField(max_digits=10, decimal_places=0, verbose_name='Precio')

    profesional_id = models.ManyToManyField(Profesional, verbose_name='Profesional')

    def __str__(self):
        return self.nombre + ' - ' + self.codigo
    objects = models.Manager()

    class Meta:
        verbose_name = 'Prestación'
        verbose_name_plural = 'Prestaciones'

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

class Examen(models.Model):

    codigo = models.CharField(max_length=20, verbose_name='Código del Examen', unique=True)
    nombre = models.CharField(max_length=100, verbose_name='Nombre del Examen')
    valor = models.DecimalField(max_digits=10, decimal_places=0, verbose_name='Valor')

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    objects = models.Manager()

    class Meta:
        verbose_name = 'Examen'
        verbose_name_plural = 'Exámenes'

class OrdenExamen(models.Model):

    numero = models.CharField(max_length=50, verbose_name='Número de Orden de Examen', unique=True)
    fecha = models.DateField(verbose_name='Fecha de la Orden')
    estado = models.CharField(max_length=1, verbose_name='Estado', choices=[('P', 'Pendiente'), ('C', 'Completado'), ('A', 'Anulado')], default='P')

    id_profesional = models.ForeignKey(Profesional, on_delete=models.CASCADE, verbose_name='Profesional')
    id_paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, verbose_name='Paciente')
    id_examen = models.ManyToManyField(Examen, verbose_name='Examen')

    def __str__(self):
        return f"Orden nro {self.numero} - Estado: {self.get_estado_display()}"

    objects = models.Manager()

    class Meta:
        verbose_name = 'Orden de Examen'
        verbose_name_plural = 'Órdenes de Exámenes'
        ordering = ['-fecha']  # Ordenar por fecha de orden descendente

class Convenio(models.Model):

    nombre = models.CharField(max_length=100, verbose_name='Nombre del Convenio')
    descuento = models.IntegerField(verbose_name='Descuento (%)', default=0)

    id_paciente = models.ManyToManyField(Paciente, verbose_name='Paciente', blank=True)

    def __str__(self):
        return self.nombre
    objects = models.Manager()

    class Meta:
        verbose_name = 'Convenio'
        verbose_name_plural = 'Convenios'

class ReservaHora(models.Model):

    fecha = models.DateField(verbose_name='Fecha de la Reserva')
    hora_inicio = models.TimeField(verbose_name='Hora de Inicio')
    hora_fin = models.TimeField(verbose_name='Hora de Fin')
    is_confirmada = models.BooleanField(default=False, verbose_name='¿Está Confirmada?')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')

    paciente_id = models.ForeignKey(Paciente, on_delete=models.CASCADE, verbose_name='Paciente')
    profesional_id = models.ForeignKey(Profesional, on_delete=models.CASCADE, verbose_name='Profesional')
    pago_id = models.ForeignKey(Pago, on_delete=models.CASCADE, verbose_name='Pago', blank=True, null=True)

    def __str__(self):
        return f"Reserva para {self.fecha} de {self.hora_inicio} a {self.hora_fin}"

    objects = models.Manager()

    class Meta:
        verbose_name = 'Reserva de Hora'
        verbose_name_plural = 'Reservas de Horas'

class Recepcionista(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Usuario')

    def __str__(self):
        return f"{self.user.email}"

    objects = models.Manager()

    class Meta:
        verbose_name = 'Recepcionista'
        verbose_name_plural = 'Recepcionistas'

class Administrador(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Usuario')

    def __str__(self):
        return f"{self.user.email}"

    objects = models.Manager()

    class Meta:
        verbose_name = 'Administrador'
        verbose_name_plural = 'Administradores'


class Agenda(models.Model):
    fecha = models.DateField(verbose_name='Fecha de la Agenda', blank=True, null=True)
    hora_inicio = models.TimeField(verbose_name='Hora de Inicio', blank=True, null=True)
    hora_fin = models.TimeField(verbose_name='Hora de Fin', blank=True, null=True)

    profesional_id = models.ForeignKey(Profesional, on_delete=models.CASCADE, verbose_name='Profesional')

    def __str__(self):
        return f"{self.fecha} - {self.profesional_id.nombre} {self.profesional_id.apellido}"

    objects = models.Manager()

    class Meta:
        verbose_name = 'Agenda'
        verbose_name_plural = 'Agendas'