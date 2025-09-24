from django.contrib import admin
from .models import *

admin.site.register(Paciente)
admin.site.register(Pago)
admin.site.register(ReservaHora)
admin.site.register(Convenio)
admin.site.register(User)

