from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List
from datetime import datetime
from database import get_db
from models.profissional import Profissional
from models.prescricao import Prescricao
from models.agenda import AgendaMedica
from models.paciente import PacienteModel
from routers.usuarios import verificar_permissao
from models.usuario import PerfilEnum
from utils.logs import registrar_log

router = APIRouter(
    prefix="/profissionais",
    tags=["Profissionais"]
)

# 1) Schemas “in-line”
class ProfissionalBase(BaseModel):
    nome: str
    email: EmailStr
    especialidade: str
    registro_conselho: str

class ProfissionalCreate(ProfissionalBase):
    pass

class ProfissionalOut(ProfissionalBase):
    id: int

    class Config:
        from_attributes = True

class AgendaIn(BaseModel):
    data_hora: datetime

class AgendaOut(AgendaIn):
    id: int
    disponivel: bool

    class Config:
        from_attributes = True

class PrescricaoIn(BaseModel):
    paciente_id: int
    data_prescricao: datetime
    medicamento: str
    posologia: str

class PrescricaoOut(PrescricaoIn):
    id: int
    profissional_id: int

    class Config:
        from_attributes = True

# 2) Endpoints

@router.post("/", response_model=ProfissionalOut)
def criar_profissional(
    dados: ProfissionalCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    if db.query(Profissional).filter_by(email=dados.email).first():
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    novo = Profissional(**dados.dict())
    db.add(novo)
    db.commit()
    db.refresh(novo)

    registrar_log(
        request, db,
        token=request.headers.get("authorization", ""),
        descricao=f"Cadastro de profissional {novo.nome}"
    )
    return novo

@router.get("/", response_model=List[ProfissionalOut])
def listar_profissionais(
    request: Request,
    db: Session = Depends(get_db)
):
    profs = db.query(Profissional).all()

    registrar_log(
        request, db,
        token=request.headers.get("authorization", ""),
        descricao="Listagem de profissionais"
    )
    return profs

@router.post(
    "/{profissional_id}/agenda",
    response_model=AgendaOut,
    dependencies=[Depends(verificar_permissao(PerfilEnum.profissional))]
)
def adicionar_agenda(
    profissional_id: int,
    entrada: AgendaIn,
    request: Request,
    db: Session = Depends(get_db)
):
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

    registrar_log(
        request, db,
        token=request.headers.get("authorization", ""),
        descricao=f"Profissional {profissional_id} adicionou agenda em {entrada.data_hora}"
    )
    return nova

@router.get(
    "/{profissional_id}/agenda",
    response_model=List[AgendaOut]
)
def listar_agenda(
    profissional_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    horarios = (
        db.query(AgendaMedica)
          .filter_by(profissional_id=profissional_id)
          .order_by(AgendaMedica.data_hora)
          .all()
    )

    registrar_log(
        request, db,
        token=request.headers.get("authorization", ""),
        descricao=f"Listagem de agenda do profissional {profissional_id}"
    )
    return horarios

@router.post(
    "/{profissional_id}/prescricoes",
    response_model=PrescricaoOut,
    dependencies=[Depends(verificar_permissao(PerfilEnum.profissional))]
)
def emitir_prescricao(
    profissional_id: int,
    dados: PrescricaoIn,
    request: Request,
    db: Session = Depends(get_db)
):
    profissional = db.query(Profissional).filter_by(id=profissional_id).first()
    paciente = db.query(PacienteModel).filter_by(id=dados.paciente_id).first()
    if not profissional or not paciente:
        raise HTTPException(status_code=404, detail="Profissional ou paciente não encontrado")

    nova = Prescricao(**dados.dict(), profissional_id=profissional_id)
    db.add(nova)
    db.commit()
    db.refresh(nova)

    registrar_log(
        request, db,
        token=request.headers.get("authorization", ""),
        descricao=f"Profissional {profissional_id} emitiu prescrição {nova.id} para paciente {paciente.id}"
    )
    return nova

@router.get(
    "/{profissional_id}/prescricoes",
    response_model=List[PrescricaoOut]
)
def listar_prescricoes(
    profissional_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    prescricoes = db.query(Prescricao).filter_by(profissional_id=profissional_id).all()

    registrar_log(
        request, db,
        token=request.headers.get("authorization", ""),
        descricao=f"Listagem de prescrições do profissional {profissional_id}"
    )
    return prescricoes