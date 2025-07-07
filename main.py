from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Banco de dados e tabelas
from database import engine
from models.paciente import Base as PacienteBase
from models.profissional import Base as ProfissionalBase
from models.usuario import Base as UsuarioBase
from models.consulta import Base as ConsultaBase
from models.prescricao import Base as PrescricaoBase
from models.telemedicina import Base as TelemedicinaBase
from models.suprimento import Base as SuprimentoBase
from models.leito import Base as LeitoBase
from models.financeiro import Base as FinanceiroBase
from models.agenda import Base as AgendaBase

# Rotas do sistema
from routers import pacientes, profissionais, usuarios, telemedicina, administracao

app = FastAPI(title="SGHSS - VidaPlus 🏥")

# 🔄 Criação das tabelas no banco
PacienteBase.metadata.create_all(bind=engine)
ProfissionalBase.metadata.create_all(bind=engine)
UsuarioBase.metadata.create_all(bind=engine)
ConsultaBase.metadata.create_all(bind=engine)
PrescricaoBase.metadata.create_all(bind=engine)
TelemedicinaBase.metadata.create_all(bind=engine)
SuprimentoBase.metadata.create_all(bind=engine)
LeitoBase.metadata.create_all(bind=engine)
FinanceiroBase.metadata.create_all(bind=engine)
AgendaBase.metadata.create_all(bind=engine)

# 🌐 CORS (pode restringir para produção)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🚀 Inclusão das rotas no app
app.include_router(usuarios.router)
app.include_router(pacientes.router)
app.include_router(profissionais.router)
app.include_router(telemedicina.router)
app.include_router(administracao.router)

# 🧪 Rota de teste
@app.get("/")
def root():
    return {"mensagem": "SGHSS VidaPlus está ativo e saudável!"}