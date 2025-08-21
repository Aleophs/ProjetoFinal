from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import List
from datetime import datetime
from sqlalchemy.orm import Session
from database import get_db
from models.leito import Leito
from models.suprimento import Suprimento
from models.financeiro import LancamentoFinanceiro
from routers.usuarios import verificar_permissao
from models.usuario import PerfilEnum
from utils.logs import registrar_log

router = APIRouter(
    prefix="/administracao",
    tags=["Administração Hospitalar"]
)

# 1) Schemas “in-line”
class SuprimentoIn(BaseModel):
    nome: str
    categoria: str
    quantidade: int
    data_validade: datetime

class SuprimentoOut(SuprimentoIn):
    id: int
    class ConfigDict:
        from_attributes = True

class LeitoIn(BaseModel):
    numero: str
    tipo: str
    unidade: str

class LeitoOut(LeitoIn):
    id: int
    ocupado: bool
    class ConfigDict:
        from_attributes = True

class LancamentoIn(BaseModel):
    tipo: str
    categoria: str
    valor: float
    data_lancamento: datetime
    unidade: str
    descricao: str

class LancamentoOut(LancamentoIn):
    id: int
    class ConfigDict:
        from_attributes = True

# 2) Endpoints
@router.post(
    "/suprimentos",
    response_model=SuprimentoOut,
    dependencies=[Depends(verificar_permissao(PerfilEnum.administrador))]
)
def cadastrar_suprimento(
    item: SuprimentoIn,
    request: Request,
    db: Session = Depends(get_db)
):
    novo = Suprimento(**item.model_dump())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    registrar_log(
        request, db,
        token=request.headers.get("authorization", ""),
        descricao=f"Cadastro de suprimento {novo.nome}"
    )
    return novo

@router.get("/suprimentos", response_model=List[SuprimentoOut])
def listar_suprimentos(
    request: Request,
    db: Session = Depends(get_db)
):
    registros = db.query(Suprimento).all()
    registrar_log(request, db, token="", descricao="Listagem de suprimentos")
    return registros

@router.post(
    "/leitos",
    response_model=LeitoOut,
    dependencies=[Depends(verificar_permissao(PerfilEnum.administrador))]
)
def cadastrar_leito(
    leito: LeitoIn,
    request: Request,
    db: Session = Depends(get_db)
):
    novo = Leito(**leito.model_dump(), ocupado=False)
    db.add(novo)
    db.commit()
    db.refresh(novo)
    registrar_log(request, db, token="", descricao=f"Cadastro de leito {novo.numero}")
    return novo

@router.get("/leitos", response_model=List[LeitoOut])
def listar_leitos(
    request: Request,
    db: Session = Depends(get_db)
):
    registros = db.query(Leito).all()
    registrar_log(request, db, token="", descricao="Listagem de leitos")
    return registros

@router.post(
    "/financeiro",
    response_model=LancamentoOut,
    dependencies=[Depends(verificar_permissao(PerfilEnum.administrador))]
)
def registrar_lancamento(
    lanc: LancamentoIn,
    request: Request,
    db: Session = Depends(get_db)
):
    novo = LancamentoFinanceiro(**lanc.model_dump())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    registrar_log(request, db, token="", descricao=f"Lançamento financeiro {novo.id}")
    return novo

@router.get("/financeiro", response_model=List[LancamentoOut])
def listar_lancamentos(
    request: Request,
    db: Session = Depends(get_db)
):
    regs = db.query(LancamentoFinanceiro).order_by(
        LancamentoFinanceiro.data_lancamento.desc()
    ).all()
    registrar_log(request, db, token="", descricao="Listagem financeiro")
    return regs

@router.get("/financeiro/resumo")
def resumo_financeiro(
    inicio: datetime,
    fim: datetime,
    request: Request,
    db: Session = Depends(get_db)
):
    if inicio > fim:
        raise HTTPException(status_code=400, detail="Período inválido")
    lancs = db.query(LancamentoFinanceiro).filter(
        LancamentoFinanceiro.data_lancamento.between(inicio, fim)
    ).all()
    receita = sum(l.valor for l in lancs if l.tipo.lower() == "receita")
    despesa = sum(l.valor for l in lancs if l.tipo.lower() == "despesa")
    saldo = receita - despesa
    registrar_log(request, db, token="", descricao="Resumo financeiro")
    return {
        "receita": receita,
        "despesa": despesa,
        "saldo": saldo,
        "periodo": f"{inicio:%d/%m/%Y} - {fim:%d/%m/%Y}"
    }