import os
from datetime import datetime, timedelta

from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# Contexto de hash (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def gerar_hash(password: str) -> str:
    """
    Gera o hash da senha usando bcrypt.
    """
    return pwd_context.hash(password)


def verificar_senha(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha em texto simples corresponde ao hash armazenado.
    """
    return pwd_context.verify(plain_password, hashed_password)


def criar_token(data: dict) -> str:
    """
    Cria um JWT com payload `data` e tempo de expiração definido em .env.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def decodificar_token(token: str) -> dict:
    """
    Decodifica o JWT e retorna o payload. Lança HTTPException em caso de falha.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )