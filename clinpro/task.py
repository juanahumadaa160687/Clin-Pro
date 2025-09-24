import pywhatkit
from celery import shared_task
from datetime import datetime, timedelta


@shared_task
def sendConfirmacion(telefono, fecha, hora_inicio):

    def sendWhatsapp(telefono):

        enlace_confirmacion = "http://127.0.0.1:8000/confirmar_hora/"

        mensaje = (f"Tiene una hora agendada para el día {fecha} a las {hora_inicio} hrs. "
                   f"Por favor, confirme su hora en: {enlace_confirmacion}")

        hora = datetime.datetime.now().hour

        minutos = datetime.datetime.now().minute + 1

        pywhatkit.sendwhatmsg(telefono, mensaje, hora, minutos, 10, True, 2)

    sendWhatsapp(telefono)

    print(f"Mensaje enviado a {telefono}")