from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from clinpro.models import User

########################################################################################################################

class ProfesionalSalud(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Usuario')
    rut = models.CharField(max_length=15, verbose_name='Rut')
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    apellido = models.CharField(max_length=100, verbose_name='Apellido')
    servicio = models.CharField(max_length=100, verbose_name='Servicio')
    especialidad = models.CharField(max_length=100, verbose_name='Especialidad', default='Sin especialidad')

    def __str__(self):
        return f"{self.nombre} {self.apellido} {self.servicio}"

    class Meta:
        verbose_name = 'Profesional Salud'
        verbose_name_plural = 'Profesionales Salud'

@receiver(post_save, sender=User)
def create_pro_salud(sender, instance, created, **kwargs):
    if created:
        pro_salud = ProfesionalSalud(user=instance)
        pro_salud.save()

post_save.connect(create_pro_salud, sender=User)

class Procedimiento(models.Model):

    codigo = models.CharField(max_length=15, verbose_name='Codigo')
    procedimiento = models.CharField(max_length=100, verbose_name='Procedimiento')
    precio = models.DecimalField(decimal_places=0, max_digits=10, verbose_name='Precio')

    profesional_salud = models.ManyToManyField(ProfesionalSalud, verbose_name='Procedimiento')

    def __str__(self):
        return f"{self.codigo} {self.procedimiento}"

    class Meta:
        verbose_name = 'Procedimiento'
        verbose_name_plural = 'Procedimientos'

class Agenda(models.Model):

    fecha = models.DateField(verbose_name='Fecha')
    hora = models.TimeField(verbose_name='Hora')
    procedimiento = models.CharField(max_length=100, verbose_name='Prestacion')

    profesional = models.ForeignKey(ProfesionalSalud, on_delete=models.CASCADE, verbose_name='Profesional')

    def __str__(self):
        return f"Agenda: {self.profesional.nombre} {self.profesional.apellido} {self.fecha}"

    class Meta:
        verbose_name = 'Agenda'
        verbose_name_plural = 'Agendas'

########################################################################################################################

class Recepcionista(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Usuario')
    rut = models.CharField(max_length=15, verbose_name='Rut')
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    apellido = models.CharField(max_length=100, verbose_name='Apellido')

    def __str__(self):
        return f"Recepcionista: {self.nombre} {self.apellido}"

    class Meta:
        verbose_name = 'Recepcionista'
        verbose_name_plural = 'Recepcionistas'

@receiver(post_save, sender=User)
def create_recepcionista(sender, instance, created, **kwargs):
    if created:
        recepcionista = Recepcionista(user=instance)
        recepcionista.save()

post_save.connect(create_recepcionista, sender=User)

########################################################################################################################

class Administracion(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Usuario')
    rut = models.CharField(max_length=15, verbose_name='Rut')
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    apellido = models.CharField(max_length=100, verbose_name='Apellido')

    def __str__(self):
        return f"Administrador: {self.nombre} {self.apellido}"

    class Meta:
        verbose_name = 'Administracion'
        verbose_name_plural = 'Administracion'

@receiver(post_save, sender=User)
def create_admin(sender, instance, created, **kwargs):
    if created:
        admin = Administracion(user=instance)
        admin.save()

post_save.connect(create_admin, sender=User)

########################################################################################################################



