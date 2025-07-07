from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from database import Base

class PacienteModel(Base):
    __tablename__ = "pacientes"

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    telefone = Column(String)
    data_nascimento = Column(DateTime)

class HistoricoClinico(Base):
    __tablename__ = "historicos_clinicos"

    id = Column(Integer, primary_key=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"))
    data_registro = Column(DateTime)
    descricao = Column(Text)
    profissional = Column(String)