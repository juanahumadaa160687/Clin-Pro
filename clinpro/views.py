from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import PacienteForm, RegisterForm, LoginForm, ProfesionalForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .decorators import allowed_users, admin_only
from .models import User, Paciente, Profesional
from .functions import getCargo


# Index page view
def index(request):
    return render(request, 'index.html')

# Login page view
def login(request):
    if request.user.is_authenticated:
        return redirect('reserva_hora')

    if request.method == 'POST':

        form = LoginForm(request.POST)

        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('reserva_hora')
        else:
            messages.error(request, 'Error: usuario o contraseña incorrectos, intente nuevamente.')
            return render(request, 'login.html', {'form': form})

    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def register(request):

    if request.method == 'POST':

        form = RegisterForm(request.POST)

        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        username = email.split('@')[0]

        if password1 != password2:
            messages.error(request, 'Las contaseñas no coinciden, intenta nuevamente')
        elif password1 == password2:
            user = User.objects.create_user(username=username, email=email, password=password1)

            group = Group.objects.get(name='Paciente')
            user.groups.add(group)

            messages.success(request, 'Usuario creado exitosamente.')
            redirect('reserva_hora')
        else:
            messages.error(request, 'Error en el registro, intente nuevamente')


    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})



#password reset page view
@login_required(login_url='login')
@allowed_users(allowed_roles=['Administrador', 'Paciente'])
def password_reset(request):


    return render(request, 'password_reset.html')


# user profile page view
@allowed_users(allowed_roles=['Paciente'])
@login_required(login_url='login')
def profile(request):

    return render(request, 'profile.html')

# reserva_hora page view
#@login_required(login_url='login')
#@allowed_users(allowed_roles=['Paciente'])
def reserva_hora(request):

    servicios = Profesional.objects.all().values('servicio').distinct()

    if request.method == 'POST' and 'servicio' in request.POST:

        servicio = request.POST.getlist('servicio', '')[0]
        print(servicio)

        especialidades = Profesional.objects.filter(servicio=servicio).values('especialidad').distinct()
        print(especialidades)

        return render(request, 'reserva_hora/reserva_hora.html',
                      {
                          'servicios': servicios,
                          'servicio': servicio,
                          'especialidades': especialidades
                      })

    elif request.method == 'POST' and 'especialidad' in request.POST:

        especialidad = request.POST.getlist('especialidad', 'a')[0]
        print(especialidad)

        profesionales = Profesional.objects.filter(especialidad=especialidad).all()
        print(profesionales)

        return render(request, 'reserva_hora/reserva_hora.html',
                      {
                          'especialidad': especialidad,
                          'pofesionales': profesionales
                      })




    if request.method == 'POST' and 'paciente' in request.POST:


        rut = request.POST['rut']
        nombre = request.POST['nombre']
        apellido = request.POST['apellido']
        direccion = request.POST['direccion']
        telefono = request.POST['telefono']
        prevision = request.POST['prevision']

        usuario = request.user

        paciente = Paciente.objects.create(rut=rut, nombre=nombre, apellido=apellido, direccion=direccion, telefono=telefono, prevision=prevision, user=usuario)

        messages.success(request, 'Datos guardados con éxito')

        return render(request, 'reserva_hora/reserva_hora.html', {'paciente': paciente})
    else:
        form = PacienteForm()
        servicio_form = ProfesionalForm()

    return render(request, 'reserva_hora/reserva_hora.html', {'form': form, 'servicios': servicios})

# logout page view
@login_required(login_url='login')
def logout(request):
    auth_logout(request)
    return redirect('index')

@login_required(login_url='login')
@allowed_users(allowed_roles=['Recepcionista'])
def recepcionista_view(request):
    return render(request, 'recepcion/dashboard_recep.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['Profesional'])
def profesional_view(request):
    return render(request, 'profesional/dashboard_prof.html')

#administrador
@login_required(login_url='login')
@admin_only
def admin_view(request):
    return render(request, 'admin/dashboard_admin.html')

@login_required(login_url='login')
@admin_only
def registro_funcionarios(request):
    return render(request, 'admin/registro_funcionarios.html')

def no_autorizado(request):
    return render(request, 'no_autorizado.html')