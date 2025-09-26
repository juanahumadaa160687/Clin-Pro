from django.contrib import admin
from .models import PersonalSalud, Servicio, Procedimiento, Agenda

admin.site.register(PersonalSalud)
admin.site.register(Servicio)
admin.site.register(Procedimiento)
admin.site.register(Agenda)