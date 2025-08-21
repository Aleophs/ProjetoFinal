from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from database import get_db
from models.usuario import Usuario, PerfilEnum
from auth import gerar_hash, verificar_senha, criar_token, decodificar_token
from utils.logs import registrar_log

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuários"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/usuarios/login")

# 1) Schemas “in-line”
class UsuarioIn(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    perfil: PerfilEnum

class UsuarioOut(BaseModel):
    id: int
    nome: str
    email: EmailStr
    perfil: PerfilEnum

    class ConfigDict:
        from_attributes = True

class LoginIn(BaseModel):
    email: EmailStr
    senha: str

# 2) Dependência de permissão
def verificar_permissao(perfil_esperado: PerfilEnum):
    def dependencia(
        token: str = Depends(oauth2_scheme),
        request: Request = None,
        db: Session = Depends(get_db)
    ):
        payload = decodificar_token(token)
        if not payload or payload.get("perfil") != perfil_esperado:
            raise HTTPException(status_code=403, detail="Acesso negado")

        registrar_log(
            request, db,
            token=token,
            descricao=f"Acesso permitido para perfil {perfil_esperado}"
        )
    return dependencia

# 3) Endpoints
@router.post(
    "/",
    response_model=UsuarioOut,
    status_code=status.HTTP_201_CREATED
)
def criar_usuario(
    usuario: UsuarioIn,
    request: Request,
    db: Session = Depends(get_db)
):
    if db.query(Usuario).filter_by(email=usuario.email).first():
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    senha_hash = gerar_hash(usuario.senha)
    novo = Usuario(**usuario.model_dump(exclude={"senha"}), senha_hash=senha_hash)
    db.add(novo)
    db.commit()
    db.refresh(novo)

    registrar_log(
        request, db,
        token=request.headers.get("authorization", ""),
        descricao=f"Usuário criado: {novo.email} (perfil {novo.perfil})"
    )
    return novo

@router.post("/login")
def login(
    dados: LoginIn,
    request: Request,
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter_by(email=dados.email).first()
    if not usuario or not verificar_senha(dados.senha, usuario.senha_hash):
        registrar_log(
            request, db,
            token="",
            descricao=f"Tentativa de login falhou para {dados.email}"
        )
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    token = criar_token({"sub": usuario.email, "perfil": usuario.perfil})
    registrar_log(
        request, db,
        token=token,
        descricao=f"Login bem-sucedido para {usuario.email}"
    )
    return {"access_token": token, "token_type": "bearer"}

@router.get(
    "/restrito",
    dependencies=[Depends(verificar_permissao(PerfilEnum.administrador))]
)
def acesso_administrador():
    return {"mensagem": "Você tem permissão de Administrador!"}