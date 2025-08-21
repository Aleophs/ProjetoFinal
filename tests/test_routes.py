import pytest
from fastapi.testclient import TestClient

def test_criar_paciente_valido(client: TestClient):
    payload = {
        "nome": "Maria Oliveira",
        "email": "maria.oliveira@example.com",
        "telefone": "11999999999",
        "data_nascimento": "1990-05-20"
    }
    r = client.post("/pacientes/", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["id"] > 0
    assert data["email"] == payload["email"]

def test_criar_paciente_email_duplicado(client: TestClient):
    payload = {
        "nome": "Maria Oliveira",
        "email": "maria.oliveira@example.com",
        "telefone": "11999999999",
        "data_nascimento": "1990-05-20"
    }
    client.post("/pacientes/", json=payload)
    r2 = client.post("/pacientes/", json=payload)
    assert r2.status_code == 409
    assert "Email já cadastrado" in r2.json()["detail"]

@pytest.mark.parametrize(
    "payload,missing_field",
    [
        ({}, "nome"),
        ({"nome": "X"}, "email"),
        ({"nome":"X","email":"a@b"}, "telefone"),
        ({"nome":"X","email":"a@b","telefone":"1"}, "data_nascimento"),
    ]
)
def test_criar_campos_obrigatorios(client: TestClient, payload, missing_field):
    r = client.post("/pacientes/", json=payload)
    assert r.status_code == 422
    errors = r.json()["detail"]
    assert any(missing_field in e["loc"] for e in errors)

def test_listar_pacientes_vazio(client: TestClient):
    r = client.get("/pacientes/")
    assert r.status_code == 200
    assert r.json() == []

def test_listar_pacientes_por_email(client: TestClient):
    p = {
        "nome":"Ana","email":"ana@teste.com","telefone":"11900000000","data_nascimento":"1992-01-01"
    }
    client.post("/pacientes/", json=p)
    r = client.get(f"/pacientes/?email={p['email']}")
    assert r.status_code == 200
    lista = r.json()
    assert len(lista) == 1
    assert lista[0]["email"] == p["email"]

def test_atualizar_paciente(client: TestClient):
    p = {
        "nome":"Beto","email":"beto@teste.com","telefone":"11911111111","data_nascimento":"1990-02-02"
    }
    post = client.post("/pacientes/", json=p)
    pid = post.json()["id"]
    update = {"nome":"Beto Silva"}
    r = client.put(f"/pacientes/{pid}", json=update)
    assert r.status_code == 200
    assert r.json()["nome"] == "Beto Silva"

def test_deletar_paciente(client: TestClient):
    p = {
        "nome":"Cris","email":"cris@teste.com","telefone":"11922222222","data_nascimento":"1991-03-03"
    }
    post = client.post("/pacientes/", json=p)
    pid = post.json()["id"]
    r = client.delete(f"/pacientes/{pid}")
    assert r.status_code == 204
    # 404 após remoção
    assert client.get(f"/pacientes/{pid}").status_code == 404