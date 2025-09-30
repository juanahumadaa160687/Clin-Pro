from django.contrib.auth.models import Group
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from administracion.forms import LoginPersonalForm, RegistroPersonalForm
from administracion.models import PersonalSalud, Servicio, Procedimiento, Agenda
from clinpro.models import User, Paciente, Convenio
import sweetify
from django.contrib.auth import login as auth_login, authenticate


def login_personal(request):

    if request.method == 'POST':
        login_form = LoginPersonalForm(request, data=request.POST)
        if login_form.is_valid():

            email = login_form.cleaned_data.get('email')
            password = login_form.cleaned_data.get('password')
            remember_me = login_form.cleaned_data.get('remember_me')

            user = authenticate(username=email, password=password)

            if user is not None:
                auth_login(request, user)

                if request.user.rol == 'administrador':
                    return render(request, 'administracion/dashboard_admin.html')
                elif request.user.rol == 'personal_salud':
                    return render(request, 'personal_salud/dashboard_personal_salud.html')
                elif request.user.rol == 'secretaria':
                    return render(request, 'recepcion/dashboard_recep.html')

                if not remember_me:
                    request.session.set_expiry(0)  # La sesión expira al cerrar el navegador

            else:
                sweetify.error(request, 'Credenciales inválidas. Por favor, inténtelo de nuevo.', button='Aceptar')
        else:
            sweetify.error(request, 'Formulario inválido. Por favor, inténtelo de nuevo.', button='Aceptar')
    else:
        login_form = LoginPersonalForm()

    return render(request, 'login_personal.html', {'login_form': login_form})

def registro(request):

    if request.method == 'POST':
        registro_personal = RegistroPersonalForm(request.POST)

        if registro_personal.is_valid():
            user =registro_personal.save(commit=False)

            user.email = registro_personal.cleaned_data.get('email')
            user.set_password(registro_personal.cleaned_data.get('password1'))
            user.nombre = registro_personal.cleaned_data.get('nombre')
            user.telefono = registro_personal.cleaned_data.get('telefono')
            user.rut = registro_personal.cleaned_data.get('rut')
            user.rol = registro_personal.cleaned_data.get('rol')

            user.save()

            group = Group.objects.get_or_create(name=user.rol)[0]
            user.groups.add(group)

            sweetify.success(request, f"Funcionario Registrado con Éxito.", button='Aceptar')
            return render(request, 'login_personal.html')
        else:
            sweetify.error(request, 'Error al registrar funcionario. Por favor, inténtelo de nuevo.', button='Aceptar')
    else:
        registro_personal = RegistroPersonalForm()

    return render(request, 'administracion/registros_admin.html', {'registro_personal': registro_personal})

def dashboard_admin(request):
    total_pacientes = Paciente.objects.count()
    total_personal_salud = PersonalSalud.objects.count()
    total_servicios = Servicio.objects.count()
    total_procedimientos = Procedimiento.objects.count()
    total_convenios = Convenio.objects.count()
    total_agendas = Agenda.objects.count()

    context = {
        'total_pacientes': total_pacientes,
        'total_personal_salud': total_personal_salud,
        'total_servicios': total_servicios,
        'total_procedimientos': total_procedimientos,
        'total_convenios': total_convenios,
        'total_agendas': total_agendas,
    }

    return render(request, 'administracion/dashboard_admin.html', context)


def