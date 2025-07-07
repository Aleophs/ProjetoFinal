from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class Leito(Base):
    __tablename__ = "leitos"

    id = Column(Integer, primary_key=True)
    numero = Column(String)
    tipo = Column(String)
    ocupado = Column(Boolean, default=False)
    unidade = Column(String)