from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from fastapi.middleware.cors import CORSMiddleware

from . import models, schemas, database, ai_service

# Inicialização do App
app = FastAPI(title="SmartBite API")

# INICIALIZAÇÃO DO BANCO DE DADOS
# Cria as tabelas automaticamente se elas não existirem
models.Base.metadata.create_all(bind=database.engine)

# Inicialização do Serviço de IA
ai = ai_service.AIService()

# Configuração de CORS para permitir que o Frontend fale com o Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependência para obter a sessão do banco de dados
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to SmartBite API"}

# --- ROTAS DE INGREDIENTES ---

@app.post("/ingredients/", response_model=schemas.Ingredient)
def create_ingredient(ingredient: schemas.IngredientCreate, db: Session = Depends(get_db)):
    db_ingredient = db.query(models.Ingredient).filter(models.Ingredient.name == ingredient.name).first()
    if db_ingredient:
        return db_ingredient
    new_ingredient = models.Ingredient(**ingredient.dict())
    db.add(new_ingredient)
    db.commit()
    db.refresh(new_ingredient)
    return new_ingredient

@app.get("/ingredients/", response_model=List[schemas.Ingredient])
def list_ingredients(db: Session = Depends(get_db)):
    return db.query(models.Ingredient).all()

# --- ROTAS DA DESPENSA (PANTRY) ---

@app.post("/pantry/", response_model=schemas.PantryItem)
def add_to_pantry(item: schemas.PantryItemCreate, db: Session = Depends(get_db)):
    new_item = models.PantryItem(**item.dict())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@app.get("/pantry/", response_model=List[schemas.PantryItem])
def list_pantry(db: Session = Depends(get_db)):
    return db.query(models.PantryItem).all()

@app.delete("/pantry/{item_id}")
def delete_pantry_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(models.PantryItem).filter(models.PantryItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return {"message": "Item removed"}

# --- ROTA DE INTELIGÊNCIA ARTIFICIAL ---

@app.get("/ai/suggest-recipe")
def get_ai_suggestion(db: Session = Depends(get_db)):
    pantry_items = db.query(models.PantryItem).all()
    if not pantry_items:
        return {"suggestion": "Your pantry is empty! Add some ingredients to get a recipe."}
    
    ingredients_list = [item.ingredient.name for item in pantry_items]
    suggestion = ai.get_recipe_suggestion(ingredients_list)
    return {"suggestion": suggestion}