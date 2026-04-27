from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine
import pytest

# FORÇA A CRIAÇÃO DO BANCO DE DADOS PARA OS TESTES
# Essencial para o ambiente do GitHub Actions
Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_read_root():
    """Verifica se a rota principal está respondendo"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to SmartBite API"}

def test_create_ingredient():
    """Verifica a criação de um ingrediente no banco de teste"""
    payload = {"name": "Test Chicken", "category": "Protein"}
    response = client.post("/ingredients/", json=payload)
    assert response.status_code in [200, 201]
    assert response.json()["name"] == "Test Chicken"

def test_list_pantry():
    """Verifica se a rota da despensa retorna uma lista"""
    response = client.get("/pantry/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_delete_nonexistent_item():
    """Verifica se o sistema lida corretamente com itens inexistentes"""
    response = client.delete("/pantry/9999")
    assert response.status_code == 404

def test_ai_suggestion_status():
    """Verifica se a rota de IA está ativa"""
    response = client.get("/ai/suggest-recipe")
    # A rota deve responder 200 OK, mesmo que retorne mensagem de erro de IA
    assert response.status_code == 200