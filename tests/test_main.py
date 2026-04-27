from fastapi.testclient import TestClient
from app.main import app
from app import models
from app.database import engine


models.Base.metadata.create_all(bind=engine)
client = TestClient(app)


def test_read_docs():
    response = client.get("/docs")
    assert response.status_code == 200

# Teste 2: Criar um ingrediente (Chicken)
def test_create_ingredient():
    response = client.post("/ingredients/", json={"name": "Test Chicken", "category": "Protein"})
    assert response.status_code == 200
    assert response.json()["name"] == "Test Chicken"

# Teste 3: Listar itens da despensa (Pantry)
def test_list_pantry():
    response = client.get("/pantry/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# Teste 4: Tentar deletar um item que não existe (Erro 404)
def test_delete_nonexistent_item():
    response = client.delete("/pantry/9999")
    assert response.status_code == 404

# Teste 5: Verificar se a rota da IA responde (Status Code)
def test_ai_suggestion_status():
    response = client.get("/ai/suggest-recipe")
    # Se a despensa estiver vazia no teste, ele pode dar 400, o que também é um comportamento esperado
    assert response.status_code in [200, 400]