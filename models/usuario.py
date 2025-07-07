from sqlalchemy import Column, Integer, String, Enum
from database import Base
import enum

class PerfilEnum(str, enum.Enum):
    administrador = "Administrador"
    profissional = "Profissional"
    paciente = "Paciente"

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    senha_hash = Column(String, nullable=False)
    perfil = Column(Enum(PerfilEnum), nullable=False)