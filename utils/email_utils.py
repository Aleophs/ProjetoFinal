import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pydantic_settings import BaseSettings
from pydantic import Field

# 1) Configuração via variáveis de ambiente
class EmailSettings(BaseSettings):
    smtp_server: str = Field(..., min_length=5)
    smtp_port: int = Field(..., ge=1)
    smtp_username: str
    smtp_password: str
    use_tls: bool = True

    model_config = {
        "env_file": "D:/ProjetoFinal/.env",
        "extra": "ignore",  # ignora variáveis não declaradas
    }

settings = EmailSettings()

# 2) Logger dedicado
logger = logging.getLogger("utils.email")
logger.setLevel(logging.INFO)  # define nível mínimo
if not logger.hasHandlers():   # evita múltiplos handlers em reload
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# 3) Função de envio de e-mail
def enviar_email(destinatario: str, assunto: str, corpo: str) -> bool:
    """
    Envia um e-mail simples (texto puro).
    Retorna True em caso de sucesso, False em falha.
    """
    msg = MIMEMultipart()
    msg["From"] = settings.smtp_username
    msg["To"] = destinatario
    msg["Subject"] = assunto
    msg.attach(MIMEText(corpo, "plain"))

    try:
        with smtplib.SMTP(settings.smtp_server, settings.smtp_port, timeout=10) as servidor:
            if settings.use_tls:
                servidor.starttls()
            servidor.login(settings.smtp_username, settings.smtp_password)
            servidor.send_message(msg)

        logger.info("E-mail enviado para %s: %s", destinatario, assunto)
        return True

    except smtplib.SMTPException as smtp_err:
        logger.error("Erro SMTP ao enviar e-mail para %s: %s", destinatario, smtp_err, exc_info=True)
    except Exception as err:
        logger.error("Erro inesperado ao enviar e-mail para %s: %s", destinatario, err, exc_info=True)

    return False