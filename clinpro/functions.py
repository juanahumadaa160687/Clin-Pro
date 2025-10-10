from email.mime.image import MIMEImage

import pywhatkit
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import datetime
from django.conf import settings
from django.utils.html import strip_tags


def conf_pago(remitente, destinatario, nombre, fecha_reserva, hora_reserva, pro_nombre, monto, m_pago, codigo_auth, orden ):

    asunto = "Confirmación de Pago y Reserva de Hora"
    remitente = remitente.lower()
    destinatarios = destinatario.lower()

    context = {
        "receiver_name": nombre,
        "fecha": datetime.datetime.now().strftime("%d/%m/%Y"),
        "fecha_reserva": fecha_reserva,
        "hora_reserva": hora_reserva,
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


def confirmacionregistro(remitentes, destinatario, nombre):
    asunto = "Confirmación de Registro"
    remitente = remitentes.lower()
    destinatarios = destinatario.lower()

    html_content = render_to_string('accounts/confirmacion_registro.html', {'nombre': nombre})
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

# Enviar mensaje de WhatsApp
def sendWhatsapp(telefono, fecha, hora_reserva, nombre):

    mensaje = f"Su hora médica para el día {fecha} a las {hora_reserva}, con el profesional {nombre} ha sido agendada correctamente"

    hora = datetime.datetime.now().hour

    minutos = datetime.datetime.now().minute + 1

    pywhatkit.sendwhatmsg(telefono, mensaje, hora, minutos, 10, True, 2)

    print("Mensaje de WhatsApp enviado correctamente")

def money_format(value):
    return "${:,.0f}".format(value).replace(",", ".")


def reserva_cancelada(remitente, destinatario, nombre_paciente, fecha_reserva, hora_reserva, profesional):
    asunto = "Cancelación de Reserva de Hora"
    remitente = remitente.lower()
    destinatarios = destinatario.lower()

    context = {
        "receiver_name": nombre_paciente,
        "fecha": datetime.datetime.now().strftime("%d/%m/%Y"),
        "fecha_reserva": fecha_reserva,
        "hora_reserva": hora_reserva,
        "profesional": profesional,
    }

    html_content = render_to_string('recepcion/reserva_cancelada_email.html', context)
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

def sendWhatsappConfirmacion(telefono, fecha_reserva, hora_reserva, nombre_profesional):

    link_confirmacion = "http://127.0.0.1:3000/confirmar_reserva/"

    mensaje = f"Le recordamos que su hora médica para el día {fecha_reserva} a las {hora_reserva}, con el profesional {nombre_profesional}, debe ser confirmada aquí {link_confirmacion}."

    hora = datetime.datetime.now().hour

    minutos = datetime.datetime.now().minute + 1

    pywhatkit.sendwhatmsg(telefono, mensaje, hora, minutos, 10, True, 2)

    print("Mensaje de WhatsApp enviado correctamente")