from email.mime.image import MIMEImage

import pywhatkit
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import datetime
from django.conf import settings
from django.utils.html import strip_tags


def conf_pago(remitente, destinatario, nombre, fecha_reserva, hora_reserva, pro_sufijo, pro_nombre, monto, m_pago, codigo_auth, orden ):

    asunto = "Confirmación de Pago y Reserva de Hora"
    remitente = remitente.lower()
    destinatarios = destinatario.lower()

    context = {
        "receiver_name": nombre,
        "fecha": datetime.datetime.now().strftime("%d/%m/%Y"),
        "fecha_reserva": fecha_reserva,
        "hora_reserva": hora_reserva,
        "profesional_sufijo": pro_sufijo,
        "profesional": pro_nombre,
        "monto": monto,
        "metodo_pago": m_pago,
        "codigo_auth": codigo_auth,
        "orden_compra": orden,
    }

    html_content = render_to_string('reserva_hora/confirmacion_pago.html', context)
    text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(
        asunto,
        text_content,
        remitente,
        [destinatarios]
    )

    msg.mixed_subtype='related'
    msg.attach_alternative(html_content, "text/html")

    image_path = settings.BASE_DIR / 'static' / 'img' / 'logo.png'
    with open(image_path, 'rb') as img:
        img = MIMEImage(img.read())
        img.add_header('Content-ID', '<logo.png>')
        img.add_header('Content-Disposition', 'inline', filename='logo.png')
        msg.attach(img)

    msg.send()

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
