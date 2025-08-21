from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from database import get_db
from models.internacao import Internacao
from models.leito import Leito
from models.paciente import Paciente
from routers.usuarios import verificar_permissao
from models.usuario import PerfilEnum
from utils.logs import registrar_log

router = APIRouter(
    prefix="/internacoes",
    tags=["Internações"]
)

# 1) Schemas “in-line”
class InternacaoIn(BaseModel):
    paciente_id: int
    leito_id: int
    data_entrada: datetime
    motivo: str

class AltaIn(BaseModel):
    data_alta: datetime

class InternacaoOut(BaseModel):
    id: int
    paciente_id: int
    leito_id: int
    data_entrada: datetime
    data_alta: Optional[datetime]
    motivo: str

    class ConfigDict:
        from_attributes = True

# 2) Endpoints
@router.post(
    "/",
    response_model=InternacaoOut,
    dependencies=[Depends(verificar_permissao(PerfilEnum.administrador))]
)
def registrar_internacao(
    dados: InternacaoIn,
    request: Request,
    db: Session = Depends(get_db)
):
    paciente = db.query(PacienteModel).filter_by(id=dados.paciente_id).first()
    leito = db.query(Leito).filter_by(id=dados.leito_id).first()

    if not paciente or not leito:
        raise HTTPException(status_code=404, detail="Paciente ou leito não encontrado")

    if leito.ocupado:
        raise HTTPException(status_code=409, detail="Leito já está ocupado")

    leito.ocupado = True
    interna = Internacao(**dados.model_dump())
    db.add(interna)
    db.commit()
    db.refresh(interna)

    registrar_log(
        request, db,
        token=request.headers.get("authorization", ""),
        descricao=f"Internação do paciente {paciente.id} no leito {leito.id}"
    )

    return interna

@router.put(
    "/{internacao_id}/alta",
    response_model=InternacaoOut,
    dependencies=[Depends(verificar_permissao(PerfilEnum.administrador))]
)
def registrar_alta(
    internacao_id: int,
    entrada: AltaIn,
    request: Request,
    db: Session = Depends(get_db)
):
    interna = db.query(Internacao).filter_by(id=internacao_id).first()
    if not interna or interna.data_alta:
        raise HTTPException(status_code=404, detail="Internação inválida")

    interna.data_alta = entrada.data_alta
    leito = db.query(Leito).filter_by(id=interna.leito_id).first()
    if leito:
        leito.ocupado = False

    db.commit()
    db.refresh(interna)

    registrar_log(
        request, db,
        token=request.headers.get("authorization", ""),
        descricao=f"Alta da internação {interna.id}, liberado leito {interna.leito_id}"
    )

    return interna

@router.get(
    "/",
    response_model=List[InternacaoOut],
    dependencies=[Depends(verificar_permissao(PerfilEnum.administrador))]
)
def listar_internacoes(
    request: Request,
    db: Session = Depends(get_db)
):
    internacoes = (
        db.query(Internacao)
          .order_by(Internacao.data_entrada.desc())
          .all()
    )

    registrar_log(
        request, db,
        token=request.headers.get("authorization", ""),
        descricao="Listagem de internações"
    )

    return internacoes