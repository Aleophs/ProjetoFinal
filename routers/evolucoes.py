from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import List
from datetime import datetime
from sqlalchemy.orm import Session
from database import get_db
from models.evolucao import EvolucaoClinica
from models.paciente import Paciente
from models.profissional import Profissional
from routers.usuarios import verificar_permissao
from models.usuario import PerfilEnum
from utils.logs import registrar_log

router = APIRouter(
    prefix="/evolucoes",
    tags=["Evoluções Médicas"]
)

# 1) Schemas “in-line”
class EvolucaoIn(BaseModel):
    paciente_id: int
    data_registro: datetime
    anotacoes: str

class EvolucaoOut(EvolucaoIn):
    id: int
    profissional_id: int

    class ConfigDict:
        from_attributes = True

# 2) Endpoints
@router.post(
    "/{profissional_id}",
    response_model=EvolucaoOut,
    dependencies=[Depends(verificar_permissao(PerfilEnum.profissional))]
)
def registrar_evolucao(
    profissional_id: int,
    entrada: EvolucaoIn,
    request: Request,
    db: Session = Depends(get_db)
):
    # valida paciente e profissional
    paciente = db.query(Paciente).filter_by(id=entrada.paciente_id).first()
    profissional = db.query(Profissional).filter_by(id=profissional_id).first()
    if not paciente or not profissional:
        raise HTTPException(status_code=404, detail="Paciente ou profissional não encontrado")

    # persiste evolução
    nova = EvolucaoClinica(**entrada.model_dump(), profissional_id=profissional_id)
    db.add(nova)
    db.commit()
    db.refresh(nova)

    # registra log de auditoria
    registrar_log(
        request, db,
        token=request.headers.get("authorization", ""),
        descricao=f"Registro de evolução paciente {paciente.id} pelo prof. {profissional.id}"
    )

    return nova

@router.get(
    "/{paciente_id}",
    response_model=List[EvolucaoOut],
    dependencies=[Depends(verificar_permissao(PerfilEnum.profissional))]
)
def listar_evolucoes(
    paciente_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    evolucoes = (
        db.query(EvolucaoClinica)
          .filter_by(paciente_id=paciente_id)
          .order_by(EvolucaoClinica.data_registro.desc())
          .all()
    )

    registrar_log(
        request, db,
        token=request.headers.get("authorization", ""),
        descricao=f"Listagem de evoluções do paciente {paciente_id}"
    )

    return evolucoes