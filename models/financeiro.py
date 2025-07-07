from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base

class LancamentoFinanceiro(Base):
    __tablename__ = "financeiro"

    id = Column(Integer, primary_key=True)
    tipo = Column(String)
    categoria = Column(String)
    valor = Column(Float)
    data_lancamento = Column(DateTime)
    unidade = Column(String)
    descricao = Column(String)