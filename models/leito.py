from sqlalchemy import (
    Column, Integer, String, Boolean
)
from sqlalchemy.orm import relationship
from database import Base

class Leito(Base):
    __tablename__ = "leitos"

    id        = Column(Integer, primary_key=True)
    numero    = Column(String(30),   index=True, nullable=False)
    tipo      = Column(String(50),   index=True, nullable=False)
    ocupado   = Column(Boolean,      server_default="false", nullable=False, index=True)
    unidade   = Column(String(50),   index=True, nullable=False)

    internacoes = relationship(
        "Internacao",
        back_populates="leito",
        cascade="all, delete-orphan"
    )