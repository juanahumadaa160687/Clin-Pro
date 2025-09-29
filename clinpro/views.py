import os
from django.contrib.auth.models import Group
from django.core import serializers
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.dateformat import time_format

from administracion.models import *
from .forms import RegistroUsuarioForm, LoginPacienteForm, PacienteModelForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .functions import enviarCorreo, sendWhatsapp, enviarconfirmacionregistro
from .models import User, Convenio, Pago, ReservaHora
from transbank.webpay.webpay_plus.transaction import Transaction
from datetime import datetime, time, timedelta
from .task import sendConfirmacion
from administracion.models import *



#Landing Page
def index(request):
    return render(request, 'index.html')

#######################################################################################################################

# Login page view
def login(request):

    if request.user.is_authenticated:
        return redirect('reserva_hora')

    form = LoginPacienteForm()

    if request.method == 'POST':

        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)

        remember_me = request.POST.get('remember_me', None)
        if remember_me is not None:
            request.session.set_expiry(1209600)
        else:
            request.session.set_expiry(0)

        if user is not None:
            auth_login(request, user)
            return redirect('reserva_hora')
        else:
            messages.error(request, 'Error: usuario o contraseña incorrectos, intente nuevamente.')
            return render(request, 'login.html', {'form': form})

    else:
        form = LoginPacienteForm()

    return render(request, 'login.html', {'form': form})

#######################################################################################################################

#Register Page View
def register(request):

    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':

        form = RegistroUsuarioForm()

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

            messages.success(request, 'Usuario creado exitosamente. Por favor, inicie sesión.')

            remitentes = os.getenv('EMAIL_HOST_USER')
            destinatario = email

            enviarconfirmacionregistro(remitentes, destinatario)

            return redirect('login')

        else:
            messages.error(request, 'Error en el registro, intente nuevamente')

    else:
        form = RegistroUsuarioForm()

    return render(request, 'register.html', {'form': form, 'success': 'Usuario creado exitosamente. Por favor, inicie sesión.'})

#######################################################################################################################

#password reset page view
#@allowed_users(allowed_roles=['Administrador', 'Paciente'])
def password_reset(request):

    return render(request, 'registration/password_reset_form.html')

def password_reset_done(request):
    return render(request, 'registration/password_reset_done.html')

def password_reset_confirm(request, uidb64, token):
    return render(request, 'registration/password_reset_confirm.html')

def password_reset_complete(request):
    return render(request, 'registration/password_reset_complete.html')

#######################################################################################################################

# user profile page view

@login_required(login_url='login')
def profile(request, id):

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


#@login_required(login_url='login')
def reserva_hora(request):

    form = PacienteModelForm()

    servicios = Servicio.objects.values('nombre').distinct()

##############_Paciente Nuevo_

    if request.method == 'POST' and 'paciente' in request.POST:

        form = PacienteModelForm(request.POST)

        if form.is_valid():
            paciente = form.save(commit=False)
            paciente.user = request.user
            paciente.save()

            messages.success(request, 'Datos del paciente guardados exitosamente.')

            servicios = Servicio.objects.values('nombre').distinct()

            return render(request, 'reserva_hora/reserva_hora.html',{'paciente': paciente, 'servicios': servicios,})

        else:
            messages.error(request, 'Error al guardar los datos del paciente. Por favor, intente nuevamente.')
            return render(request, 'reserva_hora/reserva_hora.html',{'form': form,})

##############_Servicio_

    elif request.method == 'POST' and 'servicio' in request.POST:

            request.session['servicio'] = request.POST['servicio']
            print(request.session['servicio'])
            especialidades_servicio = PersonalSalud.objects.filter(servicio__nombre=request.session['servicio']).values('especialidad').distinct()
            ls = list(especialidades_servicio)
            print(ls)
            request.session['especialidades_servicio'] = ls
            print(
                request.session['especialidades_servicio']
            )

            return render(request, 'reserva_hora/reserva_hora.html', {'especialidades': request.session['especialidades_servicio'],})

##############_Especialidad_

    elif request.method == 'POST' and 'especialidad' in request.POST:

        request.session['especialidad'] = request.POST['especialidad']
        print(request.session['especialidad'])

        profesionales_especialidad = list(PersonalSalud.objects.filter(especialidad=request.session['especialidad']).values('id', 'nombre').distinct())
        print(profesionales_especialidad)

        return render(request, 'reserva_hora/reserva_hora.html', {'profesionales': profesionales_especialidad,})

##############_Profesional_

    elif request.method == 'POST' and 'profesional' in request.POST:

        request.session['profesional'] = request.POST['profesional']
        print(request.session['profesional'])

        request.session['nombre_pro'] = PersonalSalud.objects.get(id=request.session['profesional']).nombre
        print(request.session['nombre_pro'])

        id_pro = request.session['profesional']
        print('ID:'+ id_pro)

        procedimientos_profesional = list(Procedimiento.objects.filter(personal_salud__id=id_pro).values('precio', 'procedimiento').distinct())

        print(procedimientos_profesional)

        return render(request, 'reserva_hora/reserva_hora.html', {'procedimientos': procedimientos_profesional,})

##############_Procedimiento_

    elif request.method == 'POST' and 'procedimiento' in request.POST:

        valor_procedimiento = request.POST['procedimiento']
        print(f"Valor procedimiento: {valor_procedimiento}")

        request.session['procedimiento'] = int(valor_procedimiento)
        print(request.session['procedimiento'])
        print(type(request.session['procedimiento']))

        request.session['subtotal'] = request.session['procedimiento']
        print(request.session['subtotal'])
        print(type(request.session['subtotal']))

        request.session['iva'] = int(request.session['subtotal'] * 0.19)
        print(request.session['iva'])

        return render(request, 'reserva_hora/reserva_hora.html', {})

##############_Agenda_

    elif request.method == 'POST' and 'fecha' in request.POST:

        request.session['fecha'] = request.POST['fecha']
        print(request.session['fecha'])

        fecha_seleccionada = datetime.strptime(request.session['fecha'], '%Y-%m-%d').date()
        print(fecha_seleccionada)

        if fecha_seleccionada.day == 5 or fecha_seleccionada.day == 6:
            messages.error(request, 'El centro clínico está cerrado los fines de semana. Por favor, seleccione un día hábil.')
            return render(request, 'reserva_hora/reserva_hora.html', {'error': 'El centro clínico está cerrado los fines de semana. Por favor, seleccione un día hábil.',})

        elif fecha_seleccionada < datetime.now().date():
            messages.error(request, 'La fecha no puede ser en el pasado. Por favor, seleccione una fecha válida.')
            return render(request, 'reserva_hora/reserva_hora.html', {'error': 'La fecha no puede ser en el pasado. Por favor, seleccione una fecha válida.',})

        profesional = request.session['profesional']
        print(profesional)

        horario_atencion = list([time(hour=h) for h in range(8, 21) if h < 13 or h > 14])
        print(horario_atencion)

        horas_ocupadas = list(Agenda.objects.filter(fecha=fecha_seleccionada, profesional_id=profesional).values_list('hora', flat=True))

        disponibles = [hora for hora in horario_atencion if hora not in horas_ocupadas]
        print(disponibles)

        return render(request, 'reserva_hora/reserva_hora.html', {'horas_disponibles': disponibles,})


    elif request.method == 'POST' and 'hora' in request.POST:

        request.session['hora'] = request.POST['hora']
        print(request.session['hora'])
        hora_seleccionada = datetime.strptime(request.session['hora'], '%H:%M').time()
        print(hora_seleccionada)

        horario_atencion = [time(hour=h) for h in range(8, 21) if h < 13 or h > 14]
        print(horario_atencion)

        horas_ocupadas = Agenda.objects.filter(fecha=request.session['fecha'], profesional_id=request.session['profesional']).values_list('hora', flat=True)
        print(horas_ocupadas)

        hora = time_format(hora_seleccionada, 'H:i')
        print(hora)

        horas_disponibles = [hora for hora in horario_atencion if hora not in horas_ocupadas]
        print(horas_disponibles)

        if hora_seleccionada not in horas_ocupadas and hora_seleccionada in horario_atencion:

            agenda = Agenda.objects.create(
                fecha=request.session['fecha'],
                hora=hora_seleccionada,
                profesional_id=request.session['profesional'],
            )
            agenda.save()

            convenios = Convenio.objects.all()

            return render(request, 'reserva_hora/reserva_hora.html', {'convenios': convenios})



    elif request.method == 'POST' and 'convenio' in request.POST:

        request.session['convenio'] = request.POST['convenio']
        descuento = Convenio.objects.get(id=request.session['convenio']).descuento
        request.session['nombre_convenio'] = Convenio.objects.get(id=request.session['convenio']).nombre
        print(descuento)
        print(type(descuento))

        subtotal = request.session['subtotal']
        iva = request.session['iva']
        print(subtotal)
        print(iva)
        print(type(subtotal))

        total_descuento = int(subtotal * (descuento / 100))
        print(total_descuento)
        total = subtotal - total_descuento
        print(total)

        def money_format(value):
            return "${:,.0f}".format(value).replace(",", ".")

        subtotal = money_format(subtotal)
        iva = money_format(iva)
        total_descuento = money_format(total_descuento)
        total_frt = money_format(total)

        buy_order = "ordenCompra12345"
        session_id = "sesion12345"
        amount = total
        return_url = "http://127.0.0.1:8000/pago_exitoso/"

        tx = Transaction.build_for_integration("597055555532", "579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C")
        resp = tx.create(buy_order, session_id, amount, return_url)

        token = resp["token"]
        url = resp["url"]

        return render(request, 'reserva_hora/reserva_hora.html', {'total': total_frt, 'iva': iva, 'descuento': total_descuento, 'subtotal': subtotal, 'nombre': nombre, 'dcto': descuento, 'token': token, 'url': url,})

    return render(request, 'reserva_hora/reserva_hora.html', {'form': form, 'servicios': servicios})

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

    convenio = request.session['nombre_convenio']

    Pago.objects.create(orden_compra=orden_compra, fecha=fecha_transaccion, monto=monto, metodo_pago=tipo_pago, is_pagado=True, convenio=convenio)

    pago = Pago.objects.get(orden_compra=orden_compra)

    profesional_hora = PersonalSalud.objects.filter(id = request.session['profesional']).values('nombre').distinct()

    ReservaHora.objects.create(fecha_reserva=request.session['fecha'], hora_reserva=request.session['hora'], is_confirmada=False, is_asistencia=False, is_cancelada=False, paciente_id=request.user.paciente.id, pago=pago)

    telefono = request.user.paciente.telefono
    fecha = datetime.strptime(request.session['fecha'], "%Y-%m-%d").date()
    hora_inicio = request.session['hora']
    fecha_ejecucion = datetime.combine(fecha - timedelta(days=5), time(10, 0))

    remitente = os.getenv('EMAIL_HOST_USER')
    destinatario = request.user.email

    sendWhatsapp(telefono, fecha, hora_inicio, profesional_hora.values('nombre'))

    enviarCorreo(remitente, destinatario, detalle_tarjeta, monto)

    sendConfirmacion(telefono, fecha, hora_inicio).apply_async(
        args=[telefono, fecha, hora_inicio],
        eta=fecha_ejecucion
    )

    request.session.clear()

    return render(request, 'reserva_hora/pago_exitoso.html',
                  {
                      'monto': monto,
                      'status': status,
                      'orden_compra': orden_compra,
                      'detalle_tarjeta': detalle_tarjeta,
                      'fecha_transaccion': fecha_transaccion,
                      'codigo_aut': codigo_aut,
                      'tipo_pago': tipo_pago
                  })


# logout page view
@login_required(login_url='login')
def logout(request):
    auth_logout(request)
    return redirect('index')

#######################################################################################################################

def no_autorizado(request):
    return render(request, 'no_autorizado.html')

#######################################################################################################################

def login_personal(request):
    return render(request, 'login_personal.html')