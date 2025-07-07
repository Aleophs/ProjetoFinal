from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List
from datetime import datetime
from database import SessionLocal
from models.profissional import Profissional
from models.prescricao import Prescricao
from models.agenda import AgendaMedica
from routers.usuarios import verificar_permissao
from models.usuario import PerfilEnum
from models.paciente import PacienteModel

router = APIRouter(prefix="/profissionais", tags=["Profissionais"])

# 🧠 Pydantic models

class ProfissionalBase(BaseModel):
    nome: str
    email: EmailStr
    especialidade: str
    registro_conselho: str

class ProfissionalCreate(ProfissionalBase): pass

class ProfissionalOut(ProfissionalBase):
    id: int
    model_config = {
        "from_attributes": True
    }

class AgendaIn(BaseModel):
    data_hora: datetime

class AgendaOut(AgendaIn):
    id: int
    disponivel: bool
    model_config = {
        "from_attributes": True
    }

class PrescricaoIn(BaseModel):
    paciente_id: int
    data_prescricao: datetime
    medicamento: str
    posologia: str

class PrescricaoOut(PrescricaoIn):
    id: int
    profissional_id: int
    model_config = {
        "from_attributes": True
    }

# 🔧 DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 👩‍⚕️ Cadastro e visualização de profissionais

@router.post("/", response_model=ProfissionalOut)
def criar_profissional(dados: ProfissionalCreate, db: Session = Depends(get_db)):
    if db.query(Profissional).filter_by(email=dados.email).first():
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    novo = Profissional(**dados.dict())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo

@router.get("/", response_model=List[ProfissionalOut])
def listar_profissionais(db: Session = Depends(get_db)):
    return db.query(Profissional).all()

# 📅 Agenda Médica

@router.post("/{profissional_id}/agenda", response_model=AgendaOut,
             dependencies=[Depends(verificar_permissao(PerfilEnum.profissional))])
def adicionar_agenda(profissional_id: int, entrada: AgendaIn, db: Session = Depends(get_db)):
    conflito = db.query(AgendaMedica).filter_by(
        profissional_id=profissional_id,
        data_hora=entrada.data_hora
    ).first()
    if conflito:
        raise HTTPException(status_code=400, detail="Horário já existe")
    nova = AgendaMedica(profissional_id=profissional_id, data_hora=entrada.data_hora)
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return nova

@router.get("/{profissional_id}/agenda", response_model=List[AgendaOut])
def listar_agenda(profissional_id: int, db: Session = Depends(get_db)):
    return db.query(AgendaMedica).filter_by(profissional_id=profissional_id).order_by(AgendaMedica.data_hora).all()

# 💊 Prescrições

@router.post("/{profissional_id}/prescricoes", response_model=PrescricaoOut,
             dependencies=[Depends(verificar_permissao(PerfilEnum.profissional))])
def emitir_prescricao(profissional_id: int, dados: PrescricaoIn, db: Session = Depends(get_db)):
    profissional = db.query(Profissional).filter_by(id=profissional_id).first()
    paciente = db.query(PacienteModel).filter_by(id=dados.paciente_id).first()

    if not profissional or not paciente:
        raise HTTPException(status_code=404, detail="Profissional ou paciente não encontrado")

    nova = Prescricao(**dados.dict(), profissional_id=profissional_id)
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return nova

@router.get("/{profissional_id}/prescricoes", response_model=List[PrescricaoOut])
def listar_prescricoes(profissional_id: int, db: Session = Depends(get_db)):
    return db.query(Prescricao).filter_by(profissional_id=profissional_id).all()