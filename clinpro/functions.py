import pywhatkit
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import datetime
from django.conf import settings

from administracion.models import PersonalSalud


# Enviar correo de confirmación de pago
def enviarCorreo(remitentes, destinatario, detalle_tarjeta, monto):
    asunto = "Confirmación de Pago"
    remitente = remitentes.lower()
    destinatarios = destinatario.lower()

    html_content = render_to_string('reserva_hora/confirmacion_pago.html', {})

    cuerpo = f"El pago realizado con la tarjeta terminada en {detalle_tarjeta}, por un monto de ${monto} fue realizado con éxito"

    mensaje = EmailMultiAlternatives(asunto, cuerpo, remitente, [destinatarios])

    mensaje.attach_alternative(html_content, 'text/html')

    mensaje.send()
    print("Correo enviado correctamente")

# Enviar correo de recuperación de contraseña
def enviarCorreoRecuperacion(remitentes,  destinatario, codigo):
    asunto = "Recuperación de Contraseña"
    remitente = remitentes.lower()
    destinatarios = destinatario.lower()

    html_content = render_to_string('password_reset.html', {'codigo': codigo, 'domain': settings.DOMAIN})

    cuerpo = f"Su código de recuperación es: {codigo}"

    mensaje = EmailMultiAlternatives(asunto, cuerpo, remitente, [destinatarios])

    mensaje.attach_alternative(html_content, 'text/html')

    mensaje.send()
    print("Correo enviado correctamente")

def enviarconfirmacionregistro(remitentes, destinatario):
    asunto = "Confirmación de Registro"
    remitente = remitentes.lower()
    destinatarios = destinatario.lower()

    link_login = "http://127.0.0.1:8000/login/"

    html_content = render_to_string('confirmacion_registro.html', {})

    cuerpo = f"Su registro en Clínica Clinicare ha sido exitoso. Ahora puede acceder a su cuenta y comenzar a utilizar nuestros servicios. Haga clic en el siguiente enlace para iniciar sesión: {link_login}"

    mensaje = EmailMultiAlternatives(asunto, cuerpo, remitente, [destinatarios])

    mensaje.attach_alternative(html_content, 'text/html')

    mensaje.send()
    print("Correo enviado correctamente")

# Enviar mensaje de WhatsApp
def sendWhatsapp(telefono, fecha, hora_inicio, nombre):

    mensaje = f"Su hora médica para el día {fecha} a las {hora_inicio}, con el profesional {nombre} ha sido agendada correctamente"

    hora = datetime.time(10, 0).hora

    minutos = datetime.time(10, 0).minute + 1

    pywhatkit.sendwhatmsg(telefono, mensaje, hora, minutos, 10, True, 2)
