from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List
from datetime import datetime
from database import SessionLocal
from models.paciente import PacienteModel, HistoricoClinico
from models.consulta import Consulta
from models.profissional import Profissional
from models.prescricao import Prescricao
from models.agenda import AgendaMedica
from utils.email import enviar_email
from routers.usuarios import verificar_permissao
from models.usuario import PerfilEnum

router = APIRouter(prefix="/pacientes", tags=["Pacientes"])

# 🧠 Models

class PacienteBase(BaseModel):
    nome: str
    email: EmailStr
    telefone: str
    data_nascimento: datetime

class PacienteCreate(PacienteBase): pass

class PacienteOut(PacienteBase):
    id: int
    model_config = {
        "from_attributes": True
    }

class HistoricoIn(BaseModel):
    data_registro: datetime
    descricao: str
    profissional: str

class HistoricoOut(HistoricoIn):
    id: int
    model_config = {
        "from_attributes": True
    }

class ConsultaIn(BaseModel):
    data_hora: datetime
    especialidade: str

class ConsultaOut(ConsultaIn):
    id: int
    profissional_id: int
    status: str
    model_config = {
        "from_attributes": True
    }

class PrescricaoPacienteOut(BaseModel):
    id: int
    data_prescricao: datetime
    medicamento: str
    posologia: str
    profissional_id: int
    model_config = {
        "from_attributes": True
    }

# 🔧 DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 🧪 Endpoints

@router.post("/", response_model=PacienteOut)
def criar_paciente(paciente: PacienteCreate, db: Session = Depends(get_db)):
    existente = db.query(PacienteModel).filter_by(email=paciente.email).first()
    if existente:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    novo = PacienteModel(**paciente.dict())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo

@router.get("/", response_model=List[PacienteOut])
def listar_pacientes(db: Session = Depends(get_db)):
    return db.query(PacienteModel).all()

@router.get("/{paciente_id}", response_model=PacienteOut)
def obter_paciente(paciente_id: int, db: Session = Depends(get_db)):
    paciente = db.query(PacienteModel).filter_by(id=paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    return paciente

@router.post("/{paciente_id}/historico", response_model=HistoricoOut)
def adicionar_historico(paciente_id: int, dado: HistoricoIn, db: Session = Depends(get_db)):
    if not db.query(PacienteModel).filter_by(id=paciente_id).first():
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    novo = HistoricoClinico(**dado.dict(), paciente_id=paciente_id)
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo

@router.get("/{paciente_id}/historico", response_model=List[HistoricoOut])
def listar_historico(paciente_id: int, db: Session = Depends(get_db)):
    return db.query(HistoricoClinico).filter_by(paciente_id=paciente_id).all()

@router.post("/{paciente_id}/consultas", response_model=ConsultaOut)
def agendar_consulta(paciente_id: int, dados: ConsultaIn, db: Session = Depends(get_db)):
    paciente = db.query(PacienteModel).filter_by(id=paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")

    profissional = db.query(Profissional).filter_by(especialidade=dados.especialidade).first()
    if not profissional:
        raise HTTPException(status_code=404, detail="Profissional não encontrado")

    horario = db.query(AgendaMedica).filter_by(
        profissional_id=profissional.id,
        data_hora=dados.data_hora,
        disponivel=True
    ).first()

    if not horario:
        raise HTTPException(status_code=409, detail="Horário indisponível")

    nova = Consulta(
        paciente_id=paciente_id,
        profissional_id=profissional.id,
        data_hora=dados.data_hora,
        especialidade=dados.especialidade
    )
    db.add(nova)
    horario.disponivel = False
    db.commit()
    db.refresh(nova)

    enviar_email(
        paciente.email,
        "Consulta Agendada",
        f"Sua consulta foi marcada para {nova.data_hora.strftime('%d/%m/%Y %H:%M')}."
    )

    return nova

@router.get("/{paciente_id}/consultas", response_model=List[ConsultaOut])
def listar_consultas(paciente_id: int, db: Session = Depends(get_db)):
    return db.query(Consulta).filter_by(paciente_id=paciente_id).all()

@router.get("/{paciente_id}/prescricoes",
            response_model=List[PrescricaoPacienteOut],
            dependencies=[Depends(verificar_permissao(PerfilEnum.paciente))])
def listar_prescricoes(paciente_id: int, db: Session = Depends(get_db)):
    return db.query(Prescricao).filter_by(paciente_id=paciente_id).all()