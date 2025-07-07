from sqlalchemy import Column, Integer, DateTime, Boolean, ForeignKey
from database import Base

class AgendaMedica(Base):
    __tablename__ = "agenda_medica"

    id = Column(Integer, primary_key=True)
    profissional_id = Column(Integer, ForeignKey("profissionais.id"))
    data_hora = Column(DateTime)
    disponivel = Column(Boolean, default=True)