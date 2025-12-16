import logging
import smtplib
import ssl
from email.message import EmailMessage
from typing import NamedTuple

logger = logging.getLogger("campusdigitalfp_email_sender")


class SendResult(NamedTuple):
    ok: bool
    error: str = ""


def send_email(
    smtp_host: str,
    smtp_port: int,
    smtp_user: str,
    smtp_password: str,
    to: str,
    subject: str,
    html: str,
    from_name: str = "",
) -> SendResult:
    """Envía el e-mail y devuelve (ok, error_msg)."""
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{from_name} <{smtp_user}>" if from_name else smtp_user
    msg["To"] = to
    msg.set_content("Tu cliente de correo no soporta HTML.")
    msg.add_alternative(html, subtype="html")

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context) as server:
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        logger.info("Envío OK -> %s", to)
        return SendResult(ok=True)
    except Exception as exc:  # Cualquier fallo SMTP
        logger.error("Envío FALLIDO -> %s : %s", to, exc)
        return SendResult(ok=False, error=str(exc))