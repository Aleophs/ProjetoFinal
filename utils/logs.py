import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Optional
from fastapi import Request
from sqlalchemy.orm import Session
from pydantic_settings import BaseSettings
from auth import decodificar_token
from models.log import LogAuditoria

# 1) Configurações de ambiente
class LogSettings(BaseSettings):
    log_file: str = "logs/app.log"
    max_bytes: int = 5 * 1024 * 1024       # 5 MB
    backup_count: int = 5
    level: str = "INFO"

    model_config = {
        "env_file": ".env",
        "extra": "ignore",  # << ignora outras variáveis no .env
    }


settings = LogSettings()

# 2) Logger de arquivo rotativo
logger = logging.getLogger("app_logger")
logger.setLevel(settings.level.upper())
handler = RotatingFileHandler(
    settings.log_file,
    maxBytes=settings.max_bytes,
    backupCount=settings.backup_count
)
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
handler.setFormatter(formatter)
logger.addHandler(handler)


def registrar_log(
    request: Request,
    db: Session,
    token: str,
    descricao: str,
    nivel: str = "INFO"
) -> None:
    """
    Registra auditoria em banco e em arquivo.
    - Captura método, endpoint, timestamp, usuário e perfil (se houver token).
    - Salva em tabela 'log_entries' e no arquivo configurado.
    """
    # 1. Extrai dados do token
    user_email: Optional[str] = None
    perfil: Optional[str] = None
    if token:
        payload = decodificar_token(token)
        if payload:
            user_email = payload.get("sub")
            perfil = payload.get("perfil")

    # 2. Grava no banco de dados
    log_entry = LogAuditoria(
        timestamp=datetime.utcnow(),
        metodo=request.method,
        endpoint=request.url.path,
        usuario_email=user_email,
        perfil=perfil,
        descricao=descricao
    )
    db.add(log_entry)
    db.commit()

    # 3. Grava no arquivo de log
    msg = (
        f"{request.method} {request.url.path} | "
        f"user={user_email or 'anon'} perfil={perfil or 'anon'} | "
        f"{descricao}"
    )
    log_fn = getattr(logger, nivel.lower(), logger.info)
    log_fn(msg)