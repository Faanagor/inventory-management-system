from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import crud
from schemas import product as product_schemas
from db.database import get_db

router = APIRouter()

@router.get("/products")
def get_products(db: Session = Depends(get_db), category: str = None, price: float = None, page: int = 1, limit: int = 10):
    return crud.get_products(db, category, price, page, limit)

@router.get("/products/{id}")
def get_product(id: int, db: Session = Depends(get_db)):
    return crud.get_product_by_id(db, id)

@router.post("/products")
def create_product(product: product_schemas.ProductCreate, db: Session = Depends(get_db)):
    return crud.create_product(db, product)

@router.put("/products/{id}")
def update_product(id: int, product: product_schemas.ProductUpdate, db: Session = Depends(get_db)):
    return crud.update_product(db, id, product)

@router.delete("/products/{id}")
def delete_product(id: int, db: Session = Depends(get_db)):
    return crud.delete_product(db, id)
