from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

SECRET_KEY = "segredo-super-seguro"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE = timedelta(hours=2)

pwd_context = CryptContext(schemes=["bcrypt"])

def gerar_hash(senha: str):
    return pwd_context.hash(senha)

def verificar_senha(senha: str, senha_hash: str):
    return pwd_context.verify(senha, senha_hash)

def criar_token(dados: dict):
    dados_copia = dados.copy()
    dados_copia.update({"exp": datetime.utcnow() + ACCESS_TOKEN_EXPIRE})
    return jwt.encode(dados_copia, SECRET_KEY, algorithm=ALGORITHM)

def decodificar_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None