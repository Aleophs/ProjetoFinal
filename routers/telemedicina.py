from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import datetime
from database import SessionLocal
from models.telemedicina import ConsultaTelemedicina
from models.paciente import PacienteModel
from models.profissional import Profissional
from routers.usuarios import verificar_permissao
from models.usuario import PerfilEnum

router = APIRouter(prefix="/telemedicina", tags=["Telemedicina"])

# 🧠 Pydantic Models

class TeleconsultaIn(BaseModel):
    paciente_id: int
    profissional_id: int
    data_hora: datetime
    link_video: str
    observacoes: str

class TeleconsultaOut(TeleconsultaIn):
    id: int
    model_config = {
        "from_attributes": True
    }

# 🔧 DB Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 💻 Agendamento de Teleconsulta

@router.post("/", response_model=TeleconsultaOut,
             dependencies=[Depends(verificar_permissao(PerfilEnum.profissional))])
def agendar_teleconsulta(entrada: TeleconsultaIn, db: Session = Depends(get_db)):
    paciente = db.query(PacienteModel).filter_by(id=entrada.paciente_id).first()
    profissional = db.query(Profissional).filter_by(id=entrada.profissional_id).first()

    if not paciente or not profissional:
        raise HTTPException(status_code=404, detail="Paciente ou profissional não encontrado")

    nova = ConsultaTelemedicina(**entrada.dict())
    db.add(nova)
    db.commit()
    db.refresh(nova)

    return nova

# 🔍 Listar consultas de um paciente

@router.get("/{paciente_id}", response_model=List[TeleconsultaOut],
            dependencies=[Depends(verificar_permissao(PerfilEnum.paciente))])
def listar_teleconsultas(paciente_id: int, db: Session = Depends(get_db)):
    return db.query(ConsultaTelemedicina).filter_by(paciente_id=paciente_id).all()