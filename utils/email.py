import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pydantic_settings import BaseSettings

# 1) Configuração via variáveis de ambiente
class EmailSettings(BaseSettings):
    smtp_server: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    use_tls: bool = True

    model_config = {
        "env_file": ".env",
        "extra": "ignore",  # << ignora outras variáveis no .env
    }


settings = EmailSettings()

# 2) Logger dedicado
logger = logging.getLogger("utils.email")


def enviar_email(destinatario: str, assunto: str, corpo: str) -> bool:
    """
    Envia um e-mail simples (texto puro).
    Retorna True em sucesso, False em falha.
    """
    msg = MIMEMultipart()
    msg["From"] = settings.smtp_username
    msg["To"] = destinatario
    msg["Subject"] = assunto
    msg.attach(MIMEText(corpo, "plain"))

    try:
        with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as servidor:
            if settings.use_tls:
                servidor.starttls()
            servidor.login(settings.smtp_username, settings.smtp_password)
            servidor.send_message(msg)
        logger.info("E-mail enviado para %s: %s", destinatario, assunto)
        return True

    except Exception as err:
        logger.error("Falha ao enviar e-mail para %s: %s", destinatario, err, exc_info=True)
        return False