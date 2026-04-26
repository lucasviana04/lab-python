from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, ai_service
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

import logging

# Configuração de Logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("smartbite.log"), 
        logging.StreamHandler() 
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="SmartBite API")
ai = ai_service.AIService()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/ingredients/", response_model=schemas.Ingredient)
def create_ingredient(ingredient: schemas.IngredientCreate, db: Session = Depends(get_db)):
    db_ingredient = models.Ingredient(**ingredient.model_dump())
    db.add(db_ingredient)
    db.commit()
    db.refresh(db_ingredient)
    return db_ingredient

@app.post("/pantry/", response_model=schemas.PantryItem)
def create_pantry_item(item: schemas.PantryItemCreate, db: Session = Depends(get_db)):
    db_item = models.PantryItem(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/pantry/")
def list_pantry_items(db: Session = Depends(get_db)):
    return db.query(models.PantryItem).all()

@app.get("/ai/suggest-recipe")
async def get_ai_suggestion(db: Session = Depends(get_db)):
    items = db.query(models.PantryItem).all()
    # Extract names from relationship
    ingredient_names = [item.ingredient.name for item in items if item.ingredient]
    
    if not ingredient_names:
        raise HTTPException(status_code=400, detail="Pantry is empty!")
        
    recipe = await ai.suggest_recipe(ingredient_names)
    return {"recipe": recipe}
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