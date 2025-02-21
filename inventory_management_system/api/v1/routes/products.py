from typing import List, Optional

from db.database import get_db
from fastapi import APIRouter, Depends
from schemas.product import ProductCreate, ProductResponse, ProductUpdate
from services.product_service import (
    create_product,
    delete_product,
    get_product_by_id,
    get_products,
    update_product,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

router = APIRouter(prefix="/products", tags=["Products"])


# Obtener todos los productos con filtros y paginación
@router.get("/", response_model=List[ProductResponse])
def read_products(
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    stock: Optional[int] = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    return get_products(db, category, min_price, max_price, stock, skip, limit)


# Obtener detalle de un producto
@router.get("/{product_id}", response_model=ProductResponse)
def read_product(product_id: str, db: Session = Depends(get_db)):
    return get_product_by_id(db, product_id)


# Crear un nuevo producto ASINCRONICAMENTE
@router.post("/", response_model=ProductResponse, status_code=201)
async def create_new_product(product: ProductCreate, db: AsyncSession = Depends(get_db)):
    return await create_product(db, product)  # ✅ AHORA SE AWAITEA


# Actualizar un producto existente
@router.put("/{product_id}", response_model=ProductResponse)
def update_existing_product(product_id: str, product_data: ProductUpdate, db: Session = Depends(get_db)):
    return update_product(db, product_id, product_data)


# Eliminar un producto
@router.delete("/{product_id}")
def delete_existing_product(product_id: str, db: Session = Depends(get_db)):
    return delete_product(db, product_id)
