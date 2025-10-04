from django.contrib import admin
from .models import PersonalSalud, Servicio, Procedimiento, Agenda, Administrador, Secretaria, PacienteNoRegistrado

admin.site.register(PersonalSalud)
admin.site.register(Servicio)
admin.site.register(Procedimiento)
admin.site.register(Agenda)
admin.site.register(Administrador)
admin.site.register(Secretaria)
admin.site.register(PacienteNoRegistrado)