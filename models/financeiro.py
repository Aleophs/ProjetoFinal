from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Numeric,
    DateTime,
    func
)
from database import Base

class LancamentoFinanceiro(Base):
    __tablename__ = "lancamentos_financeiros"

    id               = Column(Integer, primary_key=True)
    tipo             = Column(String(30), index=True, nullable=False)
    categoria        = Column(String(50), index=True, nullable=False)
    valor            = Column(Numeric(12, 2), nullable=False)
    data_lancamento  = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )
    unidade          = Column(String(50), nullable=True)
    descricao        = Column(Text, nullable=True)