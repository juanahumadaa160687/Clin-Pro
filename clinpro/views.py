from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.contrib import messages
from administracion.models import *
from .forms import RegisterForm, LoginForm, PacienteForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .decorators import allowed_users
from .models import User, Convenio, ReservaHora, Pago, Paciente
from transbank.webpay.webpay_plus.transaction import Transaction
import pywhatkit
from datetime import datetime, time
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


#Landing Page
def index(request):
    return render(request, 'index.html')

#######################################################################################################################

# Login page view
def login(request):

    if request.user.is_authenticated:
        return redirect('reserva_hora')

    if request.method == 'POST':

        form = LoginForm()

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

#######################################################################################################################

#Register Page View
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
            redirect('login')
        else:
            messages.error(request, 'Error en el registro, intente nuevamente')

    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})

#######################################################################################################################

#password reset page view
@login_required(login_url='login')
@allowed_users(allowed_roles=['Administrador', 'Paciente'])
def password_reset(request):


    return render(request, 'password_reset.html')

#######################################################################################################################

# user profile page view
@allowed_users(allowed_roles=['Paciente'])
@login_required(login_url='login')
def profile(request):

    return render(request, 'profile.html')

#######################################################################################################################

def edit_profile(request):
    return render(request, 'edit_profile.html')

#######################################################################################################################

def delete_profile(request):
    user = request.user
    user.delete()
    messages.success(request, 'Tu cuenta ha sido eliminada exitosamente.')
    return redirect('index')

#######################################################################################################################

# reserva_hora page view
#@login_required(login_url='login')
#@allowed_users(allowed_roles=['Paciente'])
def reserva_hora(request):

    ##############Servicios#######################################################################################

    servicios = ProfesionalSalud.objects.values('servicio').distinct()

    if request.method == 'POST' and 'servicio' in request.POST:

        request.session['servicio'] = request.POST.getlist('servicio')[0]
        print(request.session['servicio'])

        especialidades = ProfesionalSalud.objects.filter(servicio=request.session['servicio']).values('especialidad').distinct()
        print(especialidades)

        return render(request, 'reserva_hora/reserva_hora.html', {
            'especialidades': especialidades,
        })

    ##############Especialidad######################################################################################

    elif request.method == 'POST' and 'especialidad' in request.POST:

        request.session['especialidad'] = request.POST.getlist('especialidad')[0]
        print(request.session['especialidad'])

        profesionales = ProfesionalSalud.objects.filter(especialidad=request.session['especialidad']).values('id', 'nombre', 'apellido').distinct()
        print(profesionales)

        return render(request, 'reserva_hora/reserva_hora.html',
                      {
                          'profesionales': profesionales,
                      })

    ##############Procedimiento######################################################################################

    elif request.method == 'POST' and 'profesional' in request.POST:

        request.session['profesional'] = request.POST.getlist('profesional')[0]
        print(request.session['profesional'])

        request.session['pro_nombre'] = ProfesionalSalud.objects.get(id=request.session['profesional']).nombre
        print(request.session['pro_nombre'])

        request.session['pro_apellido'] = ProfesionalSalud.objects.get(id=request.session['profesional']).apellido
        print(request.session['pro_apellido'])

        profesional_id = request.session['profesional']
        print(profesional_id)

        procedimientos = Procedimiento.objects.prefetch_related('profesional_id').filter(profesional_id=profesional_id)
        print(procedimientos)

        for procedimiento in procedimientos:
            for profesional_id in procedimiento.profesional_salud.all():
                print(procedimiento.procedimiento, procedimiento.precio, procedimiento.codigo)

        return render(request, 'reserva_hora/reserva_hora.html',
                      {
                          'procedimientos': procedimientos,
                      })

    ##############Procedimiento######################################################################################

    elif request.method == 'POST' and 'procedimiento' in request.POST:

        valor_procedimiento = request.POST.getlist('procedimiento')[0]

        request.session['procedimiento'] = int(valor_procedimiento)
        print(request.session['procedimiento'])

        request.session['subtotal'] = request.session['procedimiento']
        print(request.session['subtotal'])

        return render(request, 'reserva_hora/reserva_hora.html',
                      {
                          'subtotal': request.session['procedimiento'],
                      })

    ##############Fecha#####################################################################################################

    elif request.method == 'POST' and 'fecha' in request.POST:

        request.session['fecha']  = request.POST.getlist('fecha')[0]

        format = "%Y-%m-%d"
        fecha_str = request.session['fecha']

        date = datetime.strptime(fecha_str, format)

        print(date)
        print(type(date))

        final_date = date.date()

        horario_disponible = Agenda.objects.filter(fecha=final_date, profesional_id=request.session['profesional']).values('hora_inicio').exists()
        print(horario_disponible)

        if horario_disponible:

            horas_no_disp = []

            horas = Agenda.objects.filter(fecha=final_date, profesional_id=request.session['profesional']).values('hora_inicio').distinct()

            for hora in horas:
                hour = hora['hora_inicio'].hour
                print(hora['hora_inicio'].hour)
                horas_no_disp.append(hour)

            print(horas_no_disp)

            horario = [8, 9, 10, 11, 12, 15, 16, 17, 18 , 19, 20]

            horas_no_disp = set(horas_no_disp)
            horario = set(horario)

            horas_disponibles = horario.union(horas_no_disp)

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

    ##############Hora######################################################################################################

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

        request.session['start'] = start_hour
        request.session['end'] = end_hour

        profesional = ProfesionalSalud.objects.get(id=request.session['profesional'])
        print(profesional)

        Agenda.objects.create(fecha=fecha, hora=start_hour, procedimiento=request.session['procedimiento'], profesional_id=profesional)

        id_paciente = request.user.pk
        print(id_paciente)

        convenios = Paciente.objects.filter(id=id_paciente).values('convenios').distinct()

        return render(request, 'reserva_hora/reserva_hora.html', {'convenios': convenios})

    ##############Convenios y Pago##########################################################################################

    elif request.method == 'POST' and 'convenio' in request.POST:

        request.session['convenio'] = request.POST.getlist('convenio')[0]
        descuento = int(request.session['convenio'])
        print(descuento)
        print(type(descuento))

        total = request.session['subtotal'] - ((descuento * request.session['subtotal'])/100)
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

    ##############Paciente Nuevo############################################################################################
    if request.method == 'POST' and 'paciente' in request.POST:

        rut = request.POST['rut']
        nombre = request.POST['nombre']
        apellido = request.POST['apellido']
        direccion = request.POST['direccion']
        telefono = request.POST['telefono']
        prevision = request.POST['prevision']
        convenio = request.POST.getlist('convenio')

        usuario = request.user

        paciente = Paciente.objects.create(rut=rut, nombre=nombre, apellido=apellido, direccion=direccion, telefono=telefono, prevision=prevision, user=usuario, convenio=convenio)

        messages.success(request, 'Datos guardados con éxito')

        return render(request, 'reserva_hora/reserva_hora.html', {'paciente': paciente})
    else:
        form = PacienteForm()

    return render(request, 'reserva_hora/reserva_hora.html',
                  {
                      'form': form,
                      'servicios': servicios,
                  })

#######################################################################################################################

# logout page view
@login_required(login_url='login')
def logout(request):
    auth_logout(request)
    return redirect('index')

#######################################################################################################################

def no_autorizado(request):
    return render(request, 'no_autorizado.html')

#######################################################################################################################

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
    tipo_pago = response['payment_type_code']
    codigo_aut = response['authorization_code']

    Pago.objects.create(orden_compra=orden_compra, fecha=fecha_transaccion, monto=monto, metodo_pago=tipo_pago, is_pagado=True)

    pago = Pago.objects.get(orden_compra=orden_compra)

    profesional_hora = ProfesionalSalud.objects.filter(id = request.session['profesional']).values('nombre', 'apellido').distinct()

    ReservaHora.objects.create(fecha=fecha_transaccion, hora_inicio=request.session['start'], hora_fin=request.session['end'], is_confirmada=True, paciente_id_id=request.user, pago_id_id=pago, profesional_id_id=profesional_hora)


    def sendWhatsapp(telefono):

        mensaje = f"Su hora médica para el día {request.session['fecha']} a las {request.session['hora']}, con el profesional {profesional_hora.values('nombre')}{profesional_hora.values('apellido')} ha sido agendada correctamente"

        hora = datetime.datetime.now().hour

        minutos = datetime.datetime.now().minute + 1

        pywhatkit.sendwhatmsg(telefono, mensaje, hora, minutos, 10, True, 2)

    sendWhatsapp(request.user.paciente.telefono)

    def enviarCorreo(remitentes, destinatario):
        asunto = "Confirmación de Pago"
        remitente = remitentes.lower()
        destinatarios = destinatario.lower()

        html_content = render_to_string('reserva_hora/confirmacion_pago.html', {})

        cuerpo = f"El pago realizado con la tarjeta terminada en {detalle_tarjeta}, por un monto de ${monto} fue realizado con éxito"

        mensaje = EmailMultiAlternatives(asunto, cuerpo, remitente, destinatarios)

        mensaje.attach_alternative(html_content, 'text/html')

        mensaje.send()
        print("Correo enviado correctamente")

    enviarCorreo('juan.pablo656@gmail.com', request.user.email)

    request.session.clear()

    return render(request, 'reserva_hora/pago_exitoso',
                  {
                      'monto': monto,
                      'status': status,
                      'orden_compra': orden_compra,
                      'detalle_tarjeta': detalle_tarjeta,
                      'fecha_transaccion': fecha_transaccion,
                      'codigo_aut': codigo_aut,
                      'tipo_pago': tipo_pago
                  })

#######################################################################################################################