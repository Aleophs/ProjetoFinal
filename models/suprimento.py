from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    CheckConstraint,
    func
)
from database import Base

class Suprimento(Base):
    __tablename__ = "suprimentos"

    id             = Column(Integer, primary_key=True)
    nome           = Column(String(100), index=True, nullable=False)
    categoria      = Column(String(50), index=True, nullable=False)
    quantidade     = Column(Integer, nullable=False)
    data_validade  = Column(
                      DateTime(timezone=True),
                      nullable=True,
                      index=True
                    )

    __table_args__ = (
        CheckConstraint("quantidade >= 0", name="chk_quantidade_nao_negativa"),
        # UniqueConstraint('nome', 'categoria', name='uq_suprimento_nome_categoria'),
    )