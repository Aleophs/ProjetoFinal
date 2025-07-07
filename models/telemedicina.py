from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from database import Base

class ConsultaTelemedicina(Base):
    __tablename__ = "consultas_telemedicina"

    id = Column(Integer, primary_key=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"))
    profissional_id = Column(Integer, ForeignKey("profissionais.id"))
    data_hora = Column(DateTime)
    link_video = Column(String)
    observacoes = Column(Text)