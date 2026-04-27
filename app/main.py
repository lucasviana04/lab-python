import logging
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Importações internas do seu projeto
from . import models, schemas, database, ai_service

# 1. Configuração de Logging (Requisito da Fase 3)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("smartbite.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 2. Inicialização do App (Definido apenas uma vez)
app = FastAPI(title="SmartBite API")

# 3. Inicialização do Serviço de IA (Gemini)
ai = ai_service.AIService()

# 4. Configuração de CORS
# Permite que o seu Frontend (index.html) acesse esta API com segurança
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. Dependência para obter a sessão do Banco de Dados
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- ENDPOINTS: INGREDIENTES (CRUD COMPLETO) ---

@app.post("/ingredients/", response_model=schemas.Ingredient)
def create_ingredient(ingredient: schemas.IngredientCreate, db: Session = Depends(get_db)):
    db_ingredient = db.query(models.Ingredient).filter(models.Ingredient.name == ingredient.name).first()
    if db_ingredient:
        raise HTTPException(status_code=400, detail="Ingredient already exists")
    
    new_ingredient = models.Ingredient(**ingredient.model_dump())
    db.add(new_ingredient)
    db.commit()
    db.refresh(new_ingredient)
    logger.info(f"Ingredient created: {new_ingredient.name}")
    return new_ingredient

@app.get("/ingredients/", response_model=List[schemas.Ingredient])
def list_ingredients(db: Session = Depends(get_db)):
    return db.query(models.Ingredient).all()

@app.put("/ingredients/{ingredient_id}", response_model=schemas.Ingredient)
def update_ingredient(ingredient_id: int, ingredient_update: schemas.IngredientUpdate, db: Session = Depends(get_db)):
    db_ingredient = db.query(models.Ingredient).filter(models.Ingredient.id == ingredient_id).first()
    if not db_ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    
    update_data = ingredient_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_ingredient, key, value)
    
    db.commit()
    db.refresh(db_ingredient)
    return db_ingredient

@app.delete("/ingredients/{ingredient_id}")
def delete_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
    db_ingredient = db.query(models.Ingredient).filter(models.Ingredient.id == ingredient_id).first()
    if not db_ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    db.delete(db_ingredient)
    db.commit()
    return {"detail": "Ingredient deleted successfully"}

# --- ENDPOINTS: PANTRY / DESPENSA (CRUD COMPLETO) ---

@app.get("/pantry/", response_model=List[schemas.PantryItem])
def list_pantry(db: Session = Depends(get_db)):
    return db.query(models.PantryItem).all()

@app.post("/pantry/", response_model=schemas.PantryItem)
def create_pantry_item(item: schemas.PantryItemCreate, db: Session = Depends(get_db)):
    new_item = models.PantryItem(**item.model_dump())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@app.put("/pantry/{item_id}", response_model=schemas.PantryItem)
def update_pantry_item(item_id: int, item_update: schemas.PantryItemUpdate, db: Session = Depends(get_db)):
    db_item = db.query(models.PantryItem).filter(models.PantryItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found in pantry")
    
    update_data = item_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/pantry/{item_id}")
def delete_pantry_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(models.PantryItem).filter(models.PantryItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found in pantry")
    db.delete(db_item)
    db.commit()
    return {"detail": "Item removed from pantry"}

# --- ENDPOINT: INTEGRAÇÃO COM IA ---

@app.get("/ai/suggest-recipe")
def get_ai_suggestion(db: Session = Depends(get_db)):
    pantry_items = db.query(models.PantryItem).all()
    if not pantry_items:
        raise HTTPException(status_code=400, detail="Pantry is empty")
    
    # Extrai os nomes dos ingredientes para enviar ao Gemini
    ingredients_list = [item.ingredient.name for item in pantry_items]
    suggestion = ai.get_recipe_suggestion(ingredients_list)
    return {"suggestion": suggestion}