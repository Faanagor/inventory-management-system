import uuid

from fastapi import HTTPException
from models.product import Product
from schemas.product import ProductCreate, ProductUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session


# Obtener todos los productos con filtros y paginación
def get_products(
    db: Session,
    category: str = None,
    min_price: float = None,
    max_price: float = None,
    stock: int = None,
    skip: int = 0,
    limit: int = 10,
):
    query = db.query(Product)
    if category:
        query = query.filter(Product.category == category)
    if min_price:
        query = query.filter(Product.price >= min_price)
    if max_price:
        query = query.filter(Product.price <= max_price)
    if stock is not None:
        query = query.filter(Product.stock >= stock)

    return query.offset(skip).limit(limit).all()


# Obtener un producto por ID
def get_product_by_id(db: Session, product_id: str):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# Crear un nuevo producto (ASYNC)
async def create_product(db: AsyncSession, product_data: ProductCreate):
    new_product = Product(
        id=str(uuid.uuid4()),
        name=product_data.name,
        description=product_data.description,
        category=product_data.category,
        price=product_data.price,
        sku=product_data.sku,
        stock=product_data.stock,
    )
    db.add(new_product)
    await db.commit()  # ✅ Ahora es asíncrono
    await db.refresh(new_product)  # ✅ También es asíncrono
    return new_product


# Actualizar producto existente
def update_product(db: Session, product_id: str, product_data: ProductUpdate):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in product_data.dict(exclude_unset=True).items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product


# Eliminar un producto
def delete_product(db: Session, product_id: str):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}
