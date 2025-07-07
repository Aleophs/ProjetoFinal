from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from database import Base

class Consulta(Base):
    __tablename__ = "consultas"

    id = Column(Integer, primary_key=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"))
    profissional_id = Column(Integer, ForeignKey("profissionais.id"))
    data_hora = Column(DateTime)
    especialidade = Column(String)
    status = Column(String, default="Agendada")