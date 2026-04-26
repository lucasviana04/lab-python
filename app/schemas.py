from pydantic import BaseModel
from datetime import date
from typing import Optional

class IngredientBase(BaseModel):
    name: str
    category: Optional[str] = None

class IngredientCreate(IngredientBase):
    pass

class Ingredient(IngredientBase):
    id: int
    class Config:
        from_attributes = True

class PantryItemBase(BaseModel):
    quantity: str
    expiry_date: date

class PantryItemCreate(PantryItemBase):
    ingredient_id: int

class PantryItem(PantryItemBase):
    id: int
    ingredient_id: int
    ingredient: Optional[Ingredient] = None 
    class Config:
        from_attributes = True

class IngredientUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None

class PantryItemUpdate(BaseModel):
    quantity: Optional[str] = None
    expiry_date: Optional[date] = None