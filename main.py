# main.py

import os
import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from logging.handlers import RotatingFileHandler

from settings import settings
from database import Base, engine

# Importe direto dos seus routers atuais
from routers.administracao   import router as administracao_router
from routers.evolucoes       import router as evolucoes_router
from routers.internacoes     import router as internacoes_router
from routers.pacientes       import router as pacientes_router
from routers.profissionais   import router as profissionais_router
from routers.telemedicina    import router as telemedicina_router
from routers.usuarios        import router as usuarios_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Garante que o diretório de logs exista
    log_dir = os.path.dirname(settings.log_file)
    os.makedirs(log_dir, exist_ok=True)

    # Configura o handler rotativo
    handler = RotatingFileHandler(
        settings.log_file,
        maxBytes=settings.max_bytes,
        backupCount=settings.backup_count
    )
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ))

    # Anexa ao logger do Uvicorn
    uvicorn_logger = logging.getLogger("uvicorn.access")
    uvicorn_logger.addHandler(handler)

    # Cria todas as tabelas (se ainda não existirem)
    Base.metadata.create_all(bind=engine)

    yield

    # Fecha o handler ao encerrar a aplicação
    handler.close()


# Cria a aplicação usando Lifespan Events
app = FastAPI(lifespan=lifespan)


# Registra seus routers com prefix e tags
app.include_router(administracao_router,   prefix="/administracao",   tags=["administracao"])
app.include_router(evolucoes_router,       prefix="/evolucoes",       tags=["evolucoes"])
app.include_router(internacoes_router,     prefix="/internacoes",     tags=["internacoes"])
app.include_router(pacientes_router,       prefix="/pacientes",       tags=["pacientes"])
app.include_router(profissionais_router,   prefix="/profissionais",   tags=["profissionais"])
app.include_router(telemedicina_router,    prefix="/telemedicina",    tags=["telemedicina"])
app.include_router(usuarios_router,        prefix="/usuarios",        tags=["usuarios"])