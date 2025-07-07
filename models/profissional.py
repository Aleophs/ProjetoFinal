from sqlalchemy import Column, Integer, String
from database import Base

class Profissional(Base):
    __tablename__ = "profissionais"

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    especialidade = Column(String)
    registro_conselho = Column(String)