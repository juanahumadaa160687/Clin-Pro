from celery import shared_task
from datetime import datetime, timedelta
from clinpro.models import Pago, ReservaHora
from administracion.models import Agenda
from clinpro.functions import reserva_cancelada, sendWhatsapp, sendWhatsappConfirmacion


@shared_task
def sendConfirmacion():

   reservas = ReservaHora.objects.filter(fecha_reserva=datetime.now().day + 3).all()

   for r in reservas:
         if not r.is_confirmada:
            sendWhatsappConfirmacion(r.user.telefono, r.fecha_reserva, r.hora_reserva, r.profesional.user.nombre)
            print(f"Mensaje de WhatsApp enviado a {r.user.nombre} para la reserva el día {r.fecha_reserva} a las {r.hora_reserva} con el profesional {r.profesional.user.nombre}.")

   print("Tarea de envío de confirmación completada.")


@shared_task
def cancelarReservasNoPagadas():

    pagos = Pago.objects.filter(is_pagado=False).all()
    for p in pagos:
        if (datetime.now().date() - p.fecha).days > 1:
            reservas = ReservaHora.objects.filter(pago=p).all()
            for r in reservas:
                agendas = Agenda.objects.filter(profesional=r.profesional).all()
                for a in agendas:
                    if a.profesional.id == r.profesional.id:
                        reserva_cancelada(p.id, r.user.email, r.user.nombre, r.profesional.user.nombre, r.fecha_reserva, r.hora_reserva)
                        a.delete()
                        print(f"Agenda con ID {a.id} eliminada por no tener confirmación de pago en 24hrs.")
                r.delete()
                print(f"Reserva con ID {r.id} cancelada por no tener confirmación de pago en 24hrs.")
            p.delete()
            print(f"Pago con ID {p.id} cancelado por no tener confirmación de pago en 24hrs.")
    print("Tarea de cancelación de reservas no confirmadas completada.")