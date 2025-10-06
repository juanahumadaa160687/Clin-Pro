import os
import random
from django.contrib.auth.models import Group
from django.core import serializers
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.dateformat import time_format

from administracion.forms import LoginPersonalForm
from administracion.models import *
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required

from .decorators import allowed_users
from .forms import LoginUserForm, RegistroUserForm
from .functions import sendWhatsapp, conf_pago, confirmacionregistro
from .models import User, Convenio, Pago, ReservaHora
from transbank.webpay.webpay_plus.transaction import Transaction
from datetime import datetime, time, timedelta, date
from .task import sendConfirmacion
from administracion.models import *
import sweetify



#Landing Page
def index(request):


    return render(request, 'index.html')

#######################################################################################################################

# login page view
def login(request):

    if request.method == 'POST':

        form = LoginUserForm()

        email = request.POST['email']
        password = request.POST['password1']

        user = authenticate(request, email=email, password=password)
        print(user)

        if user is not None:

            rol = User.objects.get(email=email).rol

            if rol == 'Administrador':
                auth_login(request, user)
                sweetify.success(request, f'Bienvenido {user.nombre}.', button='Aceptar', timer=3000, persistent='Ok', icon='success')
                return redirect('dashboard')

            elif rol == 'PersonalSalud':
                auth_login(request, user)
                sweetify.success(request, f'Bienvenido {user.nombre}.', button='Aceptar', timer=3000, persistent='Ok', icon='success')
                return redirect('dashboard_fichas')

            elif rol == 'Secretaria':
                auth_login(request, user)
                sweetify.success(request, f'Bienvenida {user.nombre}.', button='Aceptar', timer=3000, persistent='Ok', icon='success')
                return render(request, 'recepcion/calendar_recepcion.html', {'form': form,})


            auth_login(request, user)

            return redirect('reserva_hora')

        else:
            sweetify.error(request, 'Usuario o contraseña incorrectos.', button='Aceptar', timer=3000, persistent='Ok', icon='error')

    else:
        form = LoginUserForm()

    return render(request, 'login.html', {'form': form})

#######################################################################################################################

def registro(request):
    if request.method == 'POST':
        form = RegistroUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.rut = form.cleaned_data.get('rut')
            user.email = form.cleaned_data.get('email')
            user.nombre = form.cleaned_data.get('nombre')
            user.telefono = form.cleaned_data.get('telefono')
            user.set_password(form.cleaned_data.get('password1'))
            user.username = user.email.split('@')[0]  # Asignar username basado en el email
            user.rol = 'Paciente'

            user.save()

            grupo_paciente, created = Group.objects.get_or_create(name='Paciente')
            user.groups.add(grupo_paciente)

            remitente = os.getenv('EMAIL_HOST_USER')
            destinatario = user.email
            nombre = user.nombre

            confirmacionregistro(remitente, destinatario, nombre)

            sweetify.success(request, 'Registro exitoso. Ahora puedes iniciar sesión.', button='Aceptar', timer=3000, persistent='Ok', icon='success')
            return redirect('login')
        else:
            sweetify.error(request, 'Error en el registro. Por favor, verifica los datos ingresados.', button='Aceptar', timer=3000, persistent='Ok', icon='error')
    else:
        form = RegistroUserForm()

    return render(request, 'register.html', {'form': form})

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
@allowed_users(allowed_roles=['Paciente'])
def profile(request, id):

    if ReservaHora.objects.filter(user_id=id).exists():
        reserva = ReservaHora.objects.filter(user_id=id).order_by('-id')
        return render(request, 'profile.html', {'reserva': reserva,})

    else:
        sweetify.info(request, 'No tienes horas reservadas aún', button='Aceptar', timer=3000, persistent='Ok', icon='info')
        return render(request, 'profile.html',)


#######################################################################################################################
@login_required(login_url='login')
@allowed_users(allowed_roles=['Paciente'])
def edit_profile(request, id):
    user = User.objects.get(id=id)

    if request.method == 'POST':
        form = RegistroUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tu perfil ha sido actualizado exitosamente.')
            return redirect('profile', id=user.id)
        else:
            sweetify.error(request, 'Error al actualizar el perfil. Por favor, verifica los datos ingresados.', button='Aceptar', timer=3000, persistent='Ok', icon='error')
    else:
        form = RegistroUserForm()

    return render(request, 'edit_profile.html', {'form': form})


#######################################################################################################################

@login_required(login_url='login')
@allowed_users(allowed_roles=['Paciente'])
def delete_profile(request, id):
    user = request.user
    user.delete()
    messages.success(request, 'Tu cuenta ha sido eliminada exitosamente.')
    return redirect('index')


@login_required(login_url='login')
@allowed_users(allowed_roles=['Paciente'])
def reserva_hora(request):

    servicios = Servicio.objects.values('nombre').distinct()

##############_Servicio_

    if request.method == 'POST' and 'servicio' in request.POST:

        request.session['servicio'] = request.POST.getlist('servicio')[0]
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

        request.session['especialidad'] = request.POST.getlist('especialidad')[0]
        print(request.session['especialidad'])

        profesionales_especialidad = list(PersonalSalud.objects.filter(especialidad=request.session['especialidad']).values('id', 'user__nombre').distinct())
        print(profesionales_especialidad)

        return render(request, 'reserva_hora/reserva_hora.html', {'profesionales': profesionales_especialidad,})

##############_Profesional_

    elif request.method == 'POST' and 'profesional' in request.POST:

        request.session['profesional'] = request.POST.getlist('profesional')[0]
        print(request.session['profesional'])

        request.session['nombre_pro'] = PersonalSalud.objects.get(id=request.session['profesional']).user.nombre
        print(request.session['nombre_pro'])

        id_pro = request.session['profesional']
        print('ID:'+ id_pro)

        procedimientos_profesional = list(Procedimiento.objects.filter(personal_salud__id=id_pro).values('precio', 'procedimiento').distinct())

        print(procedimientos_profesional)

        return render(request, 'reserva_hora/reserva_hora.html', {'procedimientos': procedimientos_profesional,})

##############_Procedimiento_

    elif request.method == 'POST' and 'procedimiento' in request.POST:

        valor_procedimiento = request.POST.getlist('procedimiento')[0]
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

        request.session['fecha'] = request.POST.getlist('fecha')[0]
        print(request.session['fecha'])

        fecha_seleccionada = datetime.strptime(request.session['fecha'], '%Y-%m-%d').date()
        print(fecha_seleccionada)

        if fecha_seleccionada.day == 5 or fecha_seleccionada.day == 6:
            sweetify.error(request, 'El centro clínico está cerrado los fines de semana. Por favor, seleccione un día hábil.', button='Aceptar', timer=3000, persistent='Ok', icon='error')
            return render(request, 'reserva_hora/reserva_hora.html', {'error': 'El centro clínico está cerrado los fines de semana. Por favor, seleccione un día hábil.',})

        elif fecha_seleccionada < datetime.now().date():
            sweetify.error(request, 'La fecha no puede ser en el pasado. Por favor, seleccione una fecha válida.', button='Aceptar', timer=3000, persistent='Ok', icon='error')
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
        #print(hora_seleccionada)

        #horario_atencion = [time(hour=h) for h in range(8, 21) if h < 13 or h > 14]
        #print(horario_atencion)

        #horas_ocupadas = Agenda.objects.filter(fecha=request.session['fecha'], profesional_id=request.session['profesional']).values_list('hora', flat=True)
        #print(horas_ocupadas)

        hora = time_format(hora_seleccionada, 'H:i')
        print(hora)

        #horas_disponibles = [hora for hora in horario_atencion if hora not in horas_ocupadas]
        #print(horas_disponibles)

        #if hora_seleccionada not in horas_ocupadas and hora_seleccionada in horario_atencion:

        agenda = Agenda.objects.create(
            fecha=request.session['fecha'],
            profesional_id=request.session['profesional'],
            hora=hora_seleccionada
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
        total = subtotal + iva - total_descuento
        print(total)

        def money_format(value):
            return "${:,.0f}".format(value).replace(",", ".")

        subtotal = money_format(subtotal)
        iva = money_format(iva)
        total_descuento = money_format(total_descuento)
        total_frt = money_format(total)

        orden_compra = random.randrange(1000000000, 9999999999)  # Generar un número aleatorio de 10 dígitos
        print(orden_compra)

        buy_order = str(orden_compra)
        session_id = "sesion12345"
        amount = total
        return_url = "http://127.0.0.1:8000/pago_exitoso/"

        tx = Transaction.build_for_integration("597055555532", "579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C")
        resp = tx.create(buy_order, session_id, amount, return_url)

        token = resp["token"]
        url = resp["url"]

        return render(request, 'reserva_hora/reserva_hora.html', {'total': total_frt, 'iva': iva, 'descuento': descuento, 'subtotal': subtotal, 'nombre': request.session.get('nombre_convenio'), 'dcto': descuento, 'token': token, 'url': url, 'total_descuento': total_descuento})

    return render(request, 'reserva_hora/reserva_hora.html', {'servicios': servicios})

#######################################################################################################################

def pago_exitoso(request):

    token = request.GET.get('token_ws')
    tx = Transaction.build_for_integration("597055555532", "579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C")
    response = tx.commit(token)

    monto = response['amount']
    status = response['status']
    orden_compra =response['buy_order']
    id_session = response['session_id']
    detalle_tarjeta = response['card_detail']
    fecha_transaccion = response['transaction_date']
    tipo_pago = response['payment_type_code']
    codigo_aut = response['authorization_code']

    convenio = Convenio.objects.get(id=request.session['convenio'])
    print(convenio)

    pagado = Pago.objects.create(orden_compra=orden_compra, fecha=date.today(), monto=monto, metodo_pago=tipo_pago, is_pagado=True, convenio=convenio)
    pago = Pago.objects.get(orden_compra=orden_compra)

    if pagado is not None:
        reserva_ok = ReservaHora.objects.create(fecha_reserva=request.session['fecha'], hora_reserva=request.session['hora'], is_confirmada=False, pago=pago, user=request.user, profesional_id=request.session['profesional'])
        reserva_ok.save()
        sweetify.success(request, 'Pago realizado exitosamente.', button='Aceptar', timer=3000, persistent='Ok', icon='success')
    else:
        Agenda.objects.filter(fecha=request.session['fecha'], hora=request.session['hora'], profesional_id=request.session['profesional']).delete()
        sweetify.error(request, 'Error en el pago, intente nuevamente.', button='Aceptar', timer=3000, persistent='Ok', icon='error')
        return redirect('reserva_hora')


    if reserva_ok is not None:
        sweetify.success(request, 'Reserva de hora realizada exitosamente.', button='Aceptar', timer=3000, persistent='Ok', icon='success')
    else:
        sweetify.error(request, 'Error en la reserva de hora, intente nuevamente.', button='Aceptar', timer=3000, persistent='Ok', icon='error')

    telefono = request.user.telefono
    fecha_reserva = datetime.strptime(request.session['fecha'], "%Y-%m-%d").date()
    hora_reserva = request.session['hora']

    remitente = os.getenv('EMAIL_HOST_USER')
    print(request.user.email)

    nombre_profesional = request.session['nombre_pro']

    conf_pago(remitente, request.user.email, request.user.nombre, request.session.get('fecha'), request.session.get('hora'), nombre_profesional, str(monto), tipo_pago, orden_compra, codigo_aut )

    sendWhatsapp(telefono, fecha_reserva, hora_reserva, nombre_profesional)

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

    return None

#######################################################################################################################
