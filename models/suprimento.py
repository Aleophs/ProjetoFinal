from sqlalchemy import Column, Integer, String, DateTime
from database import Base

class Suprimento(Base):
    __tablename__ = "suprimentos"

    id = Column(Integer, primary_key=True)
    nome = Column(String)
    categoria = Column(String)
    quantidade = Column(Integer)
    data_validade = Column(DateTime)