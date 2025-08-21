from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import datetime
from database import get_db
from models.telemedicina import ConsultaTelemedicina
from models.paciente import Paciente
from models.profissional import Profissional
from routers.usuarios import verificar_permissao
from models.usuario import PerfilEnum
from utils.logs import registrar_log

router = APIRouter(
    prefix="/telemedicina",
    tags=["Telemedicina"]
)

# 1) Schemas “in-line”
class TeleconsultaIn(BaseModel):
    paciente_id: int
    profissional_id: int
    data_hora: datetime
    link_video: str
    observacoes: str

class TeleconsultaOut(TeleconsultaIn):
    id: int

    class ConfigDict:
        from_attributes = True

# 2) Endpoints

@router.post(
    "/",
    response_model=TeleconsultaOut,
    dependencies=[Depends(verificar_permissao(PerfilEnum.profissional))]
)
def agendar_teleconsulta(
    entrada: TeleconsultaIn,
    request: Request,
    db: Session = Depends(get_db)
):
    paciente = db.query(PacienteModel).filter_by(id=entrada.paciente_id).first()
    profissional = db.query(Profissional).filter_by(id=entrada.profissional_id).first()
    if not paciente or not profissional:
        raise HTTPException(status_code=404, detail="Paciente ou profissional não encontrado")

    nova = ConsultaTelemedicina(**entrada.model_dump())
    db.add(nova)
    db.commit()
    db.refresh(nova)

    registrar_log(
        request, db,
        token=request.headers.get("authorization", ""),
        descricao=(
            f"Teleconsulta agendada: paciente {paciente.id}, "
            f"profissional {profissional.id} em {entrada.data_hora}"
        )
    )
    return nova

@router.get(
    "/{paciente_id}",
    response_model=List[TeleconsultaOut],
    dependencies=[Depends(verificar_permissao(PerfilEnum.paciente))]
)
def listar_teleconsultas(
    paciente_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    consultas = (
        db.query(ConsultaTelemedicina)
          .filter_by(paciente_id=paciente_id)
          .order_by(ConsultaTelemedicina.data_hora.desc())
          .all()
    )

    registrar_log(
        request, db,
        token=request.headers.get("authorization", ""),
        descricao=f"Listagem de teleconsultas do paciente {paciente_id}"
    )
    return consultas