import os
import smtplib

from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


def enviar_correo_invitacion(
    correo_destino: str,
    nombre_empleado: str,
    enlace_invitacion: str
):
    mensaje = EmailMessage()

    mensaje["Subject"] = "Invitación al Sistema de Ingreso de Personal"
    mensaje["To"] = correo_destino

    mensaje.set_content(
        f"""
Hola {nombre_empleado},

Has sido invitado al Sistema de Ingreso de Personal de PluriOne.

Para crear tu contraseña y comenzar tu proceso de ingreso, utiliza el siguiente enlace:

{enlace_invitacion}

Este enlace tiene una vigencia máxima de 72 horas.

Si no reconoces esta invitación, puedes ignorar este correo.

Saludos,
Recursos Humanos
PluriOne - Develop Talent & Technology
"""
    )

    mensaje["From"] = EMAIL_USER

    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as servidor:
        servidor.starttls()
        servidor.login(EMAIL_USER, EMAIL_PASSWORD)
        servidor.send_message(mensaje)

def enviar_correo_recuperacion(
    correo_destino: str,
    enlace_recuperacion: str
):
    mensaje = EmailMessage()

    mensaje["Subject"] = "Recuperación de contraseña - Sistema de Ingreso de Personal"
    mensaje["To"] = correo_destino
    mensaje["From"] = EMAIL_USER

    mensaje.set_content(
        f"""
Hola,

Se solicitó la recuperación de contraseña para tu cuenta
del Sistema de Ingreso de Personal de PluriOne.

Para establecer una nueva contraseña, utiliza el siguiente enlace:

{enlace_recuperacion}

Este enlace tiene una vigencia de 1 hora.

Si no solicitaste recuperar tu contraseña, puedes ignorar este correo.

Saludos,
Sistema de Ingreso de Personal
PluriOne - Develop Talent & Technology
"""
    )

    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as servidor:
        servidor.starttls()
        servidor.login(EMAIL_USER, EMAIL_PASSWORD)
        servidor.send_message(mensaje)