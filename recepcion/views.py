import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from sweetify import sweetify

from administracion.models import Servicio, PersonalSalud, Agenda
from clinpro.decorators import allowed_users
from clinpro.functions import reserva_cancelada
from clinpro.models import ReservaHora, Pago
from recepcion.forms import PacienteNoRegistradoForm
from recepcion.models import NoRegistrado


# Create your views here.
#@login_required(login_url='login')
#@allowed_users(allowed_roles=['Secretaria'])
def reservas_view(request):

    form = PacienteNoRegistradoForm()

    ruts = NoRegistrado.objects.values('rut')
    print(ruts)

    if request.method == 'POST' and 'search' in request.POST:

        rut = request.POST.getlist('search')[0]
        print(rut)

        try:
            paciente = NoRegistrado.objects.filter(rut=rut).values('rut', 'nombre', 'telefono', 'email').first()
            print(f"Paciente encontrado: {paciente}")
            sweetify.success(request, 'Paciente encontrado', button='Aceptar', timer=3000)
            return render(request, 'recepcion/reservas_recepcion.html', {'paciente': paciente})

        except NoRegistrado.DoesNotExist:
            print("Paciente no encontrado")
            sweetify.error(request, 'Paciente no encontrado. Por favor, ingrese sus datos.', button='Aceptar', timer=3000)
            return render(request, 'recepcion/reservas_recepcion.html', {'form': form})


    elif request.method == 'POST' and 'noregistro' in request.POST:

            rut = request.POST.get('rut')
            nombre = request.POST.get('nombre')
            email = request.POST.get('email')
            telefono = request.POST.get('telefono')
            rol = 'Paciente'

            paciente = NoRegistrado.objects.create(
                nombre=nombre,
                rut=rut,
                telefono=telefono,
                email=email,
                rol=rol
            )

            paciente.save()

            if paciente is None:
                sweetify.error(request, 'Error al registrar paciente. Intente nuevamente.', button='Aceptar', timer=3000)
                return render(request, 'recepcion/reservas_recepcion.html', {'form': form})


            print(nombre, rut, telefono, email, rol)
            sweetify.success(request, 'Paciente registrado exitosamente.', button='Aceptar', timer=3000)
            return redirect('reservas')


    return render(request, 'recepcion/reservas_recepcion.html', {'form': form, 'ruts': ruts})

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

#@login_required(login_url='login')
#@allowed_users(allowed_roles=['Secretaria'])
def pagos_view(request):

    pagos = Pago.objects.values('id', 'monto', 'fecha__month', 'metodo_pago', 'is_pagado')
    print(pagos)

    meses=['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

    data=[]
    for pago in pagos:
        data.append({
            'id': pago['id'],
            'monto': pago['monto'],
            'fecha': meses[pago['fecha__month']-1],
            'metodo_pago': pago['metodo_pago'],
            'is_pagado': 'Sí' if pago['is_pagado'] else 'No'
        })
    print(data)

    def cancelar_pago():
        pago = Pago.objects.filter(fecha__month=datetime.datetime.now().month, fecha__year=datetime.datetime.now().year).all()
        reserva = ReservaHora.objects.filter(pago__in=pago).all()
        agenda = Agenda.objects.filter(profesional__reservahora__in=reserva).all()
        for p in pago:
            if not p.is_pagado and (datetime.datetime.now().date() - p.fecha).days > 1:
                for r in reserva:
                    if r.pago.id == p.id:
                        for a in agenda:
                            if a.profesional.id == r.profesional.id:
                                reserva_cancelada(p.id, r.user.email, r.user.nombre, r.profesional.user.nombre, r.fecha_reserva, r.hora_reserva)
                                a.delete()
                                print(f"Agenda con ID {a.id} eliminada por no ser confirmada en 1 días.")
                        r.delete()
                        print(f"Reserva con ID {r.id} cancelada por no ser confirmada en 1 días.")
                p.delete()
                print(f"Pago con ID {p.id} cancelado por no ser confirmado en 1 días.")

    if request.method == 'POST' and 'confirmar' in request.POST:

        pago_id = request.POST.get('confirmar')
        print(pago_id)

        pago = get_object_or_404(Pago, pk=pago_id)
        print(pago)

        pago.is_pagado = True
        pago.save()

        sweetify.success(request, 'Pago confirmado exitosamente.', button='Aceptar', timer=3000)
        return redirect('pagos_recepcion')

    return render(request, 'recepcion/pagos_recepcion.html', {'pagos': data})

@login_required(login_url='login')
@allowed_users(allowed_roles=['Secretaria'])
def editar_reserva_view(request, reserva_id, profesional_id):

    reserva = get_object_or_404(ReservaHora, pk=reserva_id)
    print(reserva)

    agenda = get_object_or_404(Agenda, profesional_id=profesional_id)
    print(agenda)

    if request.method == 'POST' and 'editar' in request.POST:

        fecha_reserva = request.POST.get('fecha_reserva')
        hora_reserva = request.POST.get('hora_reserva')

        agenda.fecha = fecha_reserva
        agenda.hora = hora_reserva

        reserva.fecha_reserva = fecha_reserva
        reserva.hora_reserva = hora_reserva

        agenda.save()
        reserva.save()

        sweetify.success(request, 'Reserva actualizada exitosamente.', button='Aceptar', timer=3000)
        return redirect('dashboard_recepcion')

    else:
        sweetify.error(request, 'Error al actualizar la reserva. Intente nuevamente.', button='Aceptar', timer=3000)

    return render(request, 'recepcion/editar_reserva.html', {'reserva': reserva, 'agenda': agenda})

@login_required(login_url='login')
@allowed_users(allowed_roles=['Secretaria'])
def delete_reserva_view(request, reserva_id):
    reserva = ReservaHora.objects.get(pk=reserva_id)
    agenda = Agenda.objects.filter(profesional__reservahora=reserva.id)
    pago = Pago.objects.get(id=reserva.pago.id)
    pago.delete()
    agenda.delete()
    reserva.delete()
    sweetify.success(request, 'Reserva eliminada exitosamente.', button='Aceptar', timer=3000)
    return redirect('dashboard_recepcion')