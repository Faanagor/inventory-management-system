import uuid

from fastapi import HTTPException
from models.product import Product
from schemas.product import ProductCreate, ProductUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


# Obtener todos los productos con filtros y paginación (ASYNC)
async def get_products(
    db: AsyncSession,
    category: str = None,
    min_price: float = None,
    max_price: float = None,
    stock: int = None,
    skip: int = 0,
    limit: int = 10,
):
    query = select(Product)
    if category:
        query = query.where(Product.category == category)
    if min_price:
        query = query.where(Product.price >= min_price)
    if max_price:
        query = query.where(Product.price <= max_price)
    if stock is not None:
        query = query.where(Product.stock >= stock)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


# Obtener un producto por ID (ASYNC)
async def get_product_by_id(db: AsyncSession, product_id: str):
    query = select(Product).where(Product.id == product_id)
    result = await db.execute(query)
    product = result.scalar_one_or_none()
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
    await db.commit()
    await db.refresh(new_product)
    return new_product


# Actualizar producto existente (ASYNC)
async def update_product(db: AsyncSession, product_id: str, product_data: ProductUpdate):
    query = select(Product).where(Product.id == product_id)
    result = await db.execute(query)
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    for key, value in product_data.dict(exclude_unset=True).items():
        setattr(product, key, value)

    await db.commit()
    await db.refresh(product)
    return product


# Eliminar un producto (ASYNC)
async def delete_product(db: AsyncSession, product_id: str):
    query = select(Product).where(Product.id == product_id)
    result = await db.execute(query)
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    await db.delete(product)
    await db.commit()
    return {"message": "Product deleted successfully"}
