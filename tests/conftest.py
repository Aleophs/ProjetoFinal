import os, sys, pytest

# 1) Garante que a raiz do projeto esteja no sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

# 2) Usa SQLite em memória, única conexão (StaticPool)
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

import database
from database import Base, get_db
from main import app

# 3) Cria engine/session de teste
test_engine = create_engine(
    os.environ["DATABASE_URL"],
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)

# 4) Monkey-patch do módulo database
database.engine = test_engine
database.SessionLocal = TestingSessionLocal

@pytest.fixture(scope="session", autouse=True)
def init_test_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="function")
def db_session():
    sess = TestingSessionLocal()
    yield sess
    sess.close()

@pytest.fixture(autouse=True)
def reset_db():
    # antes do teste, derruba e recria todas as tabelas
    Base.metadata.drop_all(bind=database.engine)
    Base.metadata.create_all(bind=database.engine)
    yield
    # opcional: limpa após o teste (já vazia se tudo rodou direito)
    Base.metadata.drop_all(bind=database.engine)


@pytest.fixture(scope="function")
def client(db_session, monkeypatch):
    # 5a) Override da dependência get_db
    def _get_db():
        yield db_session
    app.dependency_overrides[get_db] = _get_db

    # 5b) Stub do get_current_user (dependência real do seu CRUD)
    from auth import get_current_user
    class DummyUser:
        id = 1
        email = "teste@example.com"
        perfil = "tester"
    monkeypatch.setattr(
        "auth.get_current_user",
        lambda: DummyUser()
    )
    app.dependency_overrides[get_current_user] = lambda: DummyUser()

    # 5c) **Monkey-patch do registrar_log**
    #    precisa mexer no módulo exato onde foi importado
    import routers.pacientes as pac_mod
    monkeypatch.setattr(
        pac_mod,
        "registrar_log",
        lambda *args, **kwargs: None
    )

    from fastapi.testclient import TestClient
    with TestClient(app) as c:
        yield c