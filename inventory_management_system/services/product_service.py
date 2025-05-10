import uuid

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from inventory_management_system.models.product import Product
from inventory_management_system.schemas.product import ProductCreate, ProductUpdate

UUID = uuid.UUID


# Obtener todos los productos con filtros y paginación (ASYNC)
async def get_products(
    db: AsyncSession,
    category: str = None,
    min_price: float = None,
    max_price: float = None,
    skip: int = 0,
    limit: int = 10,
):
    query = select(Product)
    if not Product.id:
        raise HTTPException(status_code=404, detail="No hay productos existentes")
    if category:
        query = query.where(Product.category == category)
    if min_price:
        query = query.where(Product.price >= min_price)
    if max_price:
        query = query.where(Product.price <= max_price)

    query = query.offset(skip).limit(limit)  # Aplicar paginación
    result = await db.execute(query)
    return result.scalars().all()


# Obtener un producto por ID (ASYNC)
async def get_product_by_id(db: AsyncSession, product_id: UUID):
    query = select(Product).where(Product.id == product_id)
    result = await db.execute(query)
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


async def create_product(db: AsyncSession, product_data: ProductCreate):
    """Crea un nuevo producto en la base de datos con validación de duplicados."""
    try:
        # Verificar si ya existe un producto con el mismo SKU o nombre
        existing_product = await db.execute(
            select(Product).where((Product.sku == product_data.sku) | (Product.name == product_data.name))
        )
        if existing_product.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Ya existe un producto con este SKU o nombre")
        # Crear el nuevo producto
        new_product = Product(
            id=uuid.uuid4(),
            name=product_data.name,
            description=product_data.description,
            category=product_data.category,
            price=product_data.price,
            sku=product_data.sku,
        )
        db.add(new_product)
        await db.commit()
        await db.refresh(new_product)
        return new_product
    except SQLAlchemyError as e:
        await db.rollback()  # Deshacer cambios si ocurre un error
        raise HTTPException(status_code=500, detail=f"Error en la base de datos: {str(e)}")


# Actualizar producto existente (ASYNC)
async def update_product(db: AsyncSession, product_id: UUID, product_data: ProductUpdate):
    if isinstance(product_id, str):
        try:
            product_id = UUID(product_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="ID de producto con formato invalido")
    query = select(Product).where(Product.id == product_id)
    result = await db.execute(query)
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    update_fields = product_data.model_dump(exclude_unset=True)
    for key, value in update_fields.items():
        setattr(product, key, value)

    await db.commit()
    await db.refresh(product)
    return product


# Eliminar un producto (ASYNC)
async def delete_product(db: AsyncSession, product_id: UUID):
    query = select(Product).where(Product.id == product_id)
    result = await db.execute(query)
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    await db.delete(product)
    await db.commit()
    return {"message": "Producto eliminado exitosamente"}
