import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from sweetify import sweetify

from administracion.models import Servicio, PersonalSalud
from clinpro.decorators import allowed_users
from clinpro.models import ReservaHora

# Create your views here.
@login_required(login_url='login')
@allowed_users(allowed_roles=['Secretaria'])
def reservas_view(request):
    return render(request, 'recepcion/reservas_recepcion.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['Secretaria'])
def calendar_view(request):

    servicios = Servicio.objects.all()
    print(servicios)

    profesionales = PersonalSalud.objects.all()
    print(profesionales)

    if request.method == "POST" and 'servicio' in request.POST:

        servicio = request.POST.getlist('servicio')[0]
        print(servicio)

        eventos = ReservaHora.objects.filter(profesional__servicio__nombre=servicio).values('fecha_reserva', 'hora_reserva', 'profesional__user__nombre', 'user__nombre', 'profesional__prefijo')
        print(eventos)


        eventos1 = []
        for event in eventos:
            eventos1.append({
                'title': f"{event['profesional__prefijo']} {event['profesional__user__nombre']} - {event['user__nombre']}",
                'start': f"{event['fecha_reserva']}T{event['hora_reserva']}",
                'end': f"{event['fecha_reserva']}T{(datetime.datetime.combine(datetime.date.min, event['hora_reserva']) + datetime.timedelta(minutes=30)).time()}",
                'allDay': False,
            })

        print(eventos1)

        return render(request, 'recepcion/calendar_recepcion.html', {'eventos': eventos1, 'servicios': servicios, 'profesionales': profesionales})

    elif request.method == 'POST' and 'personal' in request.POST:

        personal = request.POST.getlist('personal')[0]
        print(personal)

        eventos = ReservaHora.objects.filter(profesional__user_id=personal).values('fecha_reserva', 'hora_reserva', 'profesional__user__nombre', 'user__nombre', 'profesional__prefijo')
        print(eventos)

        eventos1 = []
        for event in eventos:
            eventos1.append({
                'title': f"{event['profesional__prefijo']} {event['profesional__user__nombre']} - {event['user__nombre']}",
                'start': f"{event['fecha_reserva']}T{event['hora_reserva']}",
                'end': f"{event['fecha_reserva']}T{(datetime.datetime.combine(datetime.date.min, event['hora_reserva']) + datetime.timedelta(minutes=30)).time()}",
                'allDay': False,
            })

        print(eventos1)

        return render(request, 'recepcion/calendar_recepcion.html', {'eventos': eventos1, 'servicios': servicios, 'profesionales': profesionales})

    return render(request, 'recepcion/calendar_recepcion.html', {'servicios': servicios, 'profesionales': profesionales})

@login_required(login_url='login')
@allowed_users(allowed_roles=['Secretaria'])
def pagos_view(request):

    return render(request, 'recepcion/pagos_recepcion.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['Secretaria'])
def validar_pago_view(request):

    return redirect('pagos_recepcion')

@login_required(login_url='login')
@allowed_users(allowed_roles=['Secretaria'])
def modificar_reserva_view(request):

    return render(request, 'recepcion/modificar_reserva.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['Secretaria'])
def editar_reserva_view(request, reserva_id):

    return render(request, 'recepcion/editar_reserva.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['Secretaria'])
def delete_reserva_view(request, reserva_id):
    return redirect('dashboard_recepcion')