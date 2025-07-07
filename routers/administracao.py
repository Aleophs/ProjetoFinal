from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import datetime
from database import SessionLocal
from models.leito import Leito
from models.suprimento import Suprimento
from models.financeiro import LancamentoFinanceiro
from routers.usuarios import verificar_permissao
from models.usuario import PerfilEnum

router = APIRouter(prefix="/administracao", tags=["Administração Hospitalar"])

# 🔧 DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 📦 Suprimentos

class SuprimentoIn(BaseModel):
    nome: str
    categoria: str
    quantidade: int
    data_validade: datetime

class SuprimentoOut(SuprimentoIn):
    id: int
    model_config = {
        "from_attributes": True
    }

@router.post("/suprimentos", response_model=SuprimentoOut,
             dependencies=[Depends(verificar_permissao(PerfilEnum.administrador))])
def cadastrar_suprimento(item: SuprimentoIn, db: Session = Depends(get_db)):
    novo = Suprimento(**item.dict())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo

@router.get("/suprimentos", response_model=List[SuprimentoOut])
def listar_suprimentos(db: Session = Depends(get_db)):
    return db.query(Suprimento).all()

# 🛏️ Leitos

class LeitoIn(BaseModel):
    numero: str
    tipo: str
    unidade: str

class LeitoOut(LeitoIn):
    id: int
    ocupado: bool
    model_config = {
        "from_attributes": True
    }

@router.post("/leitos", response_model=LeitoOut,
             dependencies=[Depends(verificar_permissao(PerfilEnum.administrador))])
def cadastrar_leito(leito: LeitoIn, db: Session = Depends(get_db)):
    novo = Leito(**leito.dict(), ocupado=False)
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo

@router.get("/leitos", response_model=List[LeitoOut])
def listar_leitos(db: Session = Depends(get_db)):
    return db.query(Leito).all()

# 💰 Financeiro

class LancamentoIn(BaseModel):
    tipo: str
    categoria: str
    valor: float
    data_lancamento: datetime
    unidade: str
    descricao: str

class LancamentoOut(LancamentoIn):
    id: int
    model_config = {
        "from_attributes": True
    }

@router.post("/financeiro", response_model=LancamentoOut,
             dependencies=[Depends(verificar_permissao(PerfilEnum.administrador))])
def registrar_lancamento(lanc: LancamentoIn, db: Session = Depends(get_db)):
    novo = LancamentoFinanceiro(**lanc.dict())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo

@router.get("/financeiro", response_model=List[LancamentoOut])
def listar_lancamentos(db: Session = Depends(get_db)):
    return db.query(LancamentoFinanceiro).order_by(LancamentoFinanceiro.data_lancamento.desc()).all()

@router.get("/financeiro/resumo")
def resumo_financeiro(inicio: datetime, fim: datetime, db: Session = Depends(get_db)):
    lancamentos = db.query(LancamentoFinanceiro).filter(
        LancamentoFinanceiro.data_lancamento.between(inicio, fim)
    ).all()

    receita = sum(l.valor for l in lancamentos if l.tipo.lower() == "receita")
    despesa = sum(l.valor for l in lancamentos if l.tipo.lower() == "despesa")
    saldo = receita - despesa

    return {
        "receita": receita,
        "despesa": despesa,
        "saldo": saldo,
        "periodo": f"{inicio.strftime('%d/%m/%Y')} - {fim.strftime('%d/%m/%Y')}"
    }