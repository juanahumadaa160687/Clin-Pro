from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from administracion.models import PersonalSalud, Servicio, Procedimiento, Agenda
from clinpro.models import User, Paciente, Convenio


def dashboard(request):
    return render(request, 'administracion/dashboard.html')

