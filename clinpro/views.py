from datetime import datetime, timedelta

from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import PacienteForm, RegisterForm, LoginForm, ProfesionalForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .decorators import allowed_users, admin_only
from .models import User, Paciente, Profesional, Prestacion, Convenio, Agenda
from transbank.webpay.webpay_plus.transaction import Transaction

from datetime import datetime, time

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

    form = PacienteForm()
    s_form = ProfesionalForm()

    servicios = Profesional.objects.values('servicio').distinct()

    print(servicios)

    if request.method == 'POST' and 'servicio' in request.POST:

        request.session['servicio'] = request.POST.getlist('servicio')[0]
        print(request.session['servicio'])

        especialidades = Profesional.objects.filter(servicio=request.session['servicio']).values('especialidad').distinct()
        print(especialidades)


        return render(request, 'reserva_hora/reserva_hora.html', {
            'especialidades': especialidades,
        })

    elif request.method == 'POST' and 'especialidad' in request.POST:

        request.session['especialidad'] = request.POST.getlist('especialidad')[0]
        print(request.session['especialidad'])

        profesionales = Profesional.objects.filter(especialidad=request.session['especialidad']).values('id', 'nombre', 'apellido').distinct()
        print(profesionales)

        return render(request, 'reserva_hora/reserva_hora.html',
                      {
                          'profesionales': profesionales,
                      })

    elif request.method == 'POST' and 'profesional' in request.POST:

        request.session['profesional'] = request.POST.getlist('profesional')[0]
        print(request.session['profesional'])

        request.session['pro_nombre'] = Profesional.objects.get(id=request.session['profesional']).nombre
        print(request.session['pro_nombre'])

        request.session['pro_apellido'] = Profesional.objects.get(id=request.session['profesional']).apellido
        print(request.session['pro_apellido'])

        profesional_id = request.session['profesional']
        print(profesional_id)

        prestaciones = Prestacion.objects.prefetch_related('profesional_id').filter(profesional_id=profesional_id)
        print(prestaciones)

        for prestacion in prestaciones:
            for profesional_id in prestacion.profesional_id.all():
                print(prestacion.nombre, prestacion.precio, prestacion.codigo)

        return render(request, 'reserva_hora/reserva_hora.html',
                      {
                          'prestaciones': prestaciones,
                      })


    elif request.method == 'POST' and 'prestacion' in request.POST:

        valor_prestacion = request.POST.getlist('prestacion')[0]

        request.session['prestacion'] = int(valor_prestacion)
        print(request.session['prestacion'])

        request.session['subtotal'] = request.session['prestacion']
        print(request.session['subtotal'])

        return render(request, 'reserva_hora/reserva_hora.html',
                      {
                          'subtotal': request.session['prestacion'],
                      })

    elif request.method == 'POST' and 'fecha' in request.POST:

        request.session['fecha']  = request.POST.getlist('fecha')[0]

        format = "%Y-%m-%d"
        fecha_str = request.session['fecha']

        date = datetime.strptime(fecha_str, format)
        print(date)
        print(type(date))

        date_date = date.date()

        horario_disponible = Agenda.objects.filter(fecha=date_date, profesional_id=request.session['profesional']).values('hora_inicio').exists()
        print(horario_disponible)

        if horario_disponible:

            horas_disp = []

            horas = Agenda.objects.filter(fecha=date_date, profesional_id=request.session['profesional']).values('hora_inicio').distinct()

            for hora in horas:
                hour = hora['hora_inicio'].hour
                print(hora['hora_inicio'].hour)
                horas_disp.append(hour)

            print(horas_disp)

            horario = [8, 9, 10, 11, 12, 15, 16, 17, 18 , 19, 20]
            horas_disponibles = []

            for h in horas_disp:
                for hr in horario:
                    if hr != h:
                        horas_disponibles.append(hr)

            print(horas_disponibles)

            hour = []

            for hd in horas_disponibles:
                initial_hours = time(hd, 00)
                final_hours = time(hd, 45)

                hours = {
                    'hora_inicio': initial_hours.hour,
                    'min_inicio': initial_hours.minute,
                    'hora_final': final_hours.hour,
                    'min_final': final_hours.minute,
                }

                hour.append(hours)

            print(hour)

            return render(request, 'reserva_hora/reserva_hora.html', {'hour': hour})

    elif request.method == 'POST' and 'hora' in request.POST:

        request.session['hora'] = request.POST.getlist('hora')[0]

        hora = int(request.session['hora'])

        fecha = request.session['fecha']

        start_hour = time(hora, 00)
        end_hour = time(hora, 45)

        s_hour = start_hour.hour
        m_hour = start_hour.minute
        h_end = end_hour.hour
        m_end = end_hour.minute

        print(s_hour, m_hour)

        request.session['hora_inicio'] = s_hour
        request.session['min_inicio'] = m_hour
        request.session['hora_final'] = h_end
        request.session['min_final'] = m_end

        profesional = Profesional.objects.get(id=request.session['profesional'])
        print(profesional)

        Agenda.objects.create(fecha=fecha, hora_inicio=start_hour, hora_fin=end_hour, profesional_id=profesional)

        id_paciente = request.user.pk
        print(id_paciente)

        convenios = Convenio.objects.prefetch_related('id_paciente').all()
        for convenio in convenios:
            for id_paciente in convenio.id_paciente.all():
                print(convenio.nombre, convenio.descuento)


        return render(request, 'reserva_hora/reserva_hora.html', {'convenios': convenios})


    elif request.method == 'POST' and 'convenio' in request.POST:

        request.session['convenio'] = request.POST.getlist('convenio')[0]
        descuento = int(request.session['convenio'])
        print(descuento)
        print(type(descuento))

        total = request.session['subtotal'] - (descuento * request.session['subtotal'])/100
        print(total)


        request.session['total'] = total

        request.session['nro_compra'] = "ordenCompra12345"
        request.session['session_key'] = "sesion12345"

        buy_order = request.session['nro_compra']
        session_id = request.session['session_key']
        amount = request.session['total']
        return_url = "http://127.0.0.1:8000/pago_exitoso/"

        tx = Transaction.build_for_integration("597055555532", "579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C")
        resp = tx.create(buy_order, session_id, amount, return_url)

        token = resp["token"]
        url = resp["url"]

        return render(request, 'reserva_hora/reserva_hora.html',
                      {
                          'token': token,
                          'url': url,
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
        s_form = ProfesionalForm()

    return render(request, 'reserva_hora/reserva_hora.html',
                  {
                      'form': form,
                      's_form': s_form,
                      'servicios': servicios,
                  })

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

def pago_exitoso(request):

    token = request.GET.get('token_ws')
    tx = Transaction.build_for_integration("597055555532", "579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C")
    response = tx.commit(token)

    monto = response['amount']
    status = response['status']
    orden_compra =response['buy_order']
    id_sesion = response['session_id']
    detalle_tarjeta = response['card_detail']
    fecha_transaccion = response['transaction_date']
    tipo_págo = response['payment_type_code']
    codigo_aut = response['authorization_code']

    request.session.clear()

    return render(request, 'reserva_hora/pago_exitoso',
                  {
                      'monto': monto,
                      'status': status,
                      'orden_compra': orden_compra,
                      'detalle_tarjeta': detalle_tarjeta,
                      'fecha_transaccion': fecha_transaccion,
                      'id_sesion': id_sesion,
                      'detalle_tajeta': detalle_tarjeta,
                      'codigo_aut': codigo_aut,
                      'tipo_pago': tipo_págo
                  })