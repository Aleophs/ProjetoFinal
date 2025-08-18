from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List
from datetime import datetime
from database import get_db
from models.paciente import PacienteModel, HistoricoClinico
from models.consulta import Consulta
from models.profissional import Profissional
from models.prescricao import Prescricao
from models.agenda import AgendaMedica
from utils.email import enviar_email
from routers.usuarios import verificar_permissao
from models.usuario import PerfilEnum
from utils.logs import registrar_log

router = APIRouter(
    prefix="/pacientes",
    tags=["Pacientes"]
)

# 1) Schemas “in-line”
class PacienteBase(BaseModel):
    nome: str
    email: EmailStr
    telefone: str
    data_nascimento: datetime

class PacienteCreate(PacienteBase):
    pass

class PacienteOut(PacienteBase):
    id: int

    class Config:
        from_attributes = True

class HistoricoIn(BaseModel):
    data_registro: datetime
    descricao: str
    profissional: str

class HistoricoOut(HistoricoIn):
    id: int

    class Config:
        from_attributes = True

class ConsultaIn(BaseModel):
    data_hora: datetime
    especialidade: str

class ConsultaOut(ConsultaIn):
    id: int
    profissional_id: int
    status: str

    class Config:
        from_attributes = True

class PrescricaoPacienteOut(BaseModel):
    id: int
    data_prescricao: datetime
    medicamento: str
    posologia: str
    profissional_id: int

    class Config:
        from_attributes = True

# 2) Endpoints
@router.post("/", response_model=PacienteOut)
def criar_paciente(
    paciente: PacienteCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    exist = db.query(PacienteModel).filter_by(email=paciente.email).first()
    if exist:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    novo = PacienteModel(**paciente.dict())
    db.add(novo)
    db.commit()
    db.refresh(novo)

    registrar_log(
        request, db,
        token=request.headers.get("authorization", ""),
        descricao=f"Cadastro de paciente {novo.nome}"
    )
    return novo

@router.get("/", response_model=List[PacienteOut])
def listar_pacientes(
    request: Request,
    db: Session = Depends(get_db)
):
    pacientes = db.query(PacienteModel).all()
    registrar_log(
        request, db,
        token=request.headers.get("authorization", ""),
        descricao="Listagem de pacientes"
    )
    return pacientes

@router.get("/{paciente_id}", response_model=PacienteOut)
def obter_paciente(
    paciente_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    paciente = db.query(PacienteModel).filter_by(id=paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")

    registrar_log(
        request, db,
        token=request.headers.get("authorization", ""),
        descricao=f"Consulta de paciente ID {paciente_id}"
    )
    return paciente

@router.post("/{paciente_id}/historico", response_model=HistoricoOut)
def adicionar_historico(
    paciente_id: int,
    dado: HistoricoIn,
    request: Request,
    db: Session = Depends(get_db)
):
    if not db.query(PacienteModel).filter_by(id=paciente_id).first():
        raise HTTPException(status_code=404, detail="Paciente não encontrado")

    novo = HistoricoClinico(**dado.dict(), paciente_id=paciente_id)
    db.add(novo)
    db.commit()
    db.refresh(novo)

    registrar_log(
        request, db,
        token=request.headers.get("authorization", ""),
        descricao=f"Registro de histórico paciente {paciente_id}"
    )
    return novo

@router.get("/{paciente_id}/historico", response_model=List[HistoricoOut])
def listar_historico(
    paciente_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    historicos = db.query(HistoricoClinico).filter_by(paciente_id=paciente_id).all()

    registrar_log(
        request, db,
        token=request.headers.get("authorization", ""),
        descricao=f"Listagem de histórico paciente {paciente_id}"
    )
    return historicos

@router.post("/{paciente_id}/consultas", response_model=ConsultaOut)
def agendar_consulta(
    paciente_id: int,
    dados: ConsultaIn,
    request: Request,
    db: Session = Depends(get_db)
):
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

    registrar_log(
        request, db,
        token=request.headers.get("authorization", ""),
        descricao=f"Agendamento de consulta {nova.id} para paciente {paciente_id}"
    )
    return nova

@router.get("/{paciente_id}/consultas", response_model=List[ConsultaOut])
def listar_consultas(
    paciente_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    consultas = db.query(Consulta).filter_by(paciente_id=paciente_id).all()

    registrar_log(
        request, db,
        token=request.headers.get("authorization", ""),
        descricao=f"Listagem de consultas paciente {paciente_id}"
    )
    return consultas

@router.delete("/{paciente_id}/consultas/{consulta_id}")
def cancelar_consulta(
    paciente_id: int,
    consulta_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    consulta = db.query(Consulta).filter_by(id=consulta_id, paciente_id=paciente_id).first()
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    if consulta.status == "Cancelada":
        raise HTTPException(status_code=400, detail="Consulta já cancelada")

    consulta.status = "Cancelada"
    horario = db.query(AgendaMedica).filter_by(
        profissional_id=consulta.profissional_id,
        data_hora=consulta.data_hora
    ).first()
    if horario:
        horario.disponivel = True
    db.commit()

    enviar_email(
        db.query(PacienteModel).filter_by(id=paciente_id).first().email,
        "Consulta Cancelada",
        "Sua consulta foi cancelada com sucesso."
    )

    registrar_log(
        request, db,
        token=request.headers.get("authorization", ""),
        descricao=f"Cancelamento de consulta {consulta_id} paciente {paciente_id}"
    )
    return {"mensagem": "Consulta cancelada e horário liberado"}

@router.get(
    "/{paciente_id}/prescricoes",
    response_model=List[PrescricaoPacienteOut],
    dependencies=[Depends(verificar_permissao(PerfilEnum.paciente))]
)
def listar_prescricoes(
    paciente_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    prescricoes = db.query(Prescricao).filter_by(paciente_id=paciente_id).all()

    registrar_log(
        request, db,
        token=request.headers.get("authorization", ""),
        descricao=f"Listagem de prescrições paciente {paciente_id}"
    )
    return prescricoes