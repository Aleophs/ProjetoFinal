import os
from pydantic_settings import BaseSettings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Generator

class DatabaseSettings(BaseSettings):
    database_url: str = "sqlite:///./app.db"
    echo: bool = False
    pool_pre_ping: bool = True

    model_config = {
        "env_file": ".env",
        "extra": "ignore",  # << ignora outras variáveis no .env
    }


# Carrega configurações do .env
settings = DatabaseSettings()

# Ajusta argumentos de conexão
if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    connect_args = {"pool_pre_ping": settings.pool_pre_ping}

# Criação do Engine SQLAlchemy
engine = create_engine(
    settings.database_url,
    echo=settings.echo,
    connect_args=connect_args
)

# Sessão padrão (síncrona)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

# Base para modelos declarativos
Base = declarative_base()

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db() -> None:
    Base.metadata.create_all(bind=engine)