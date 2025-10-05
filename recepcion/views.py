import datetime

from django.shortcuts import render

from administracion.models import Servicio
from clinpro.models import ReservaHora


# Create your views here.

def reservas_view(request):

    return render(request, 'recepcion/reservas_recepcion.html')

def calendar_view(request):

    servicios = Servicio.objects.all()

    if request.method == "POST" and 'servicio' in request.POST:
        servicio = request.POST.get('servicio')

        eventos = ReservaHora.objects.filter(profesional__servicio__nombre=servicio).values('fecha_reserva', 'hora_reserva', 'profesional__user__nombre', 'paciente__user__nombre', 'profesional__prefijo')
        print(eventos)


        eventos1 = []
        for event in eventos:
            eventos1.append({
                'title': f"{event['profesional__prefijo']} {event['profesional__user__nombre']} - {event['paciente__user__nombre']}",
                'start': f"{event['fecha_reserva']}T{event['hora_reserva']}",
                'end': f"{event['fecha_reserva']}T{(datetime.datetime.combine(datetime.date.min, event['hora_reserva']) + datetime.timedelta(minutes=30)).time()}",
                'allDay': False,
            })

        print(eventos1)

        return render(request, 'recepcion/calendar_recepcion.html', {'eventos': eventos1, 'servicios': servicios})

    return render(request, 'recepcion/calendar_recepcion.html', {'servicios': servicios})

def pagos_view(request):

    return render(request, 'recepcion/pagos_recepcion.html')