from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from database import Base

class Prescricao(Base):
    __tablename__ = "prescricoes"

    id = Column(Integer, primary_key=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"))
    profissional_id = Column(Integer, ForeignKey("profissionais.id"))
    data_prescricao = Column(DateTime)
    medicamento = Column(String)
    posologia = Column(Text)