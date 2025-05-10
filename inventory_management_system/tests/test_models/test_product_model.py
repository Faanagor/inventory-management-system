import uuid
from typing import List

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from inventory_management_system.models import Product


@pytest.mark.asyncio
async def test_create_product(async_db_session: AsyncSession, sample_products: List[Product]) -> None:
    """Verifica que un producto se pueda crear y almacenar en la base de datos."""
    product: Product = sample_products[0]

    async_db_session.add(product)
    await async_db_session.commit()
    await async_db_session.refresh(product)

    assert product.id is not None
    assert isinstance(product.id, uuid.UUID)
    assert product.name == "Varilla Corrugada"
    assert product.description == "Refuerzo estructural de concreto."
    assert product.category == "Construcción"
    assert product.price == 25.50
    assert product.sku == "VARILLA123"


@pytest.mark.asyncio
async def test_create_many_products(async_db_session: AsyncSession, sample_products: List[Product]) -> None:
    """Verifica que se puedan crear múltiples productos."""
    async_db_session.add_all(sample_products)
    await async_db_session.commit()

    result = await async_db_session.execute(select(Product))
    stored_products: List[Product] = result.scalars().all()

    assert len(stored_products) == len(sample_products)


@pytest.mark.asyncio
async def test_read_product(async_db_session: AsyncSession, sample_products: List[Product]) -> None:
    """Verifica que se pueda leer un producto correctamente."""
    product = sample_products[0]  # Producto precargado en la base de datos
    # product_id = UUID(str(product.id))
    result = await async_db_session.execute(select(Product).where(Product.id == product.id))
    db_product = result.scalars().first()
    await async_db_session.commit()
    assert db_product is not None
    assert db_product.sku == "VARILLA123"
    assert db_product.category == "Construcción"
    assert db_product.price == 25.50


@pytest.mark.asyncio
async def test_update_product(async_db_session: AsyncSession, sample_products: List[Product]) -> None:
    """Verifica que se pueda actualizar un producto correctamente."""
    product = sample_products[0]
    async_db_session.add(product)
    await async_db_session.commit()
    await async_db_session.refresh(product)
    product.price = 30.00
    await async_db_session.commit()
    result = await async_db_session.execute(select(Product).where(Product.id == product.id))
    updated_product = result.scalars().first()
    assert updated_product is not None
    assert updated_product.price == 30.00


@pytest.mark.asyncio
async def test_delete_product(async_db_session: AsyncSession, sample_products: List[Product]) -> None:
    """Verifica que un producto pueda ser eliminado correctamente."""
    product: Product = sample_products[0]
    await async_db_session.commit()
    await async_db_session.delete(product)
    await async_db_session.commit()
    result = await async_db_session.execute(select(Product).where(Product.id == product.id))
    deleted_product = result.scalars().first()
    assert deleted_product is None


@pytest.mark.asyncio
async def test_unique_sku(async_db_session: AsyncSession) -> None:
    """Verifica que no se puedan insertar dos productos con el mismo SKU."""
    product1 = Product(
        name="Varilla Corrugada",
        description="Refuerzo estructural.",
        category="Construcción",
        price=25.50,
        sku="VARILLA123",
    )
    product2 = Product(
        name="Otra Varilla",
        description="Otra varilla diferente.",
        category="Construcción",
        price=30.00,
        sku="VARILLA123",
    )
    async_db_session.add(product1)
    await async_db_session.commit()
    async_db_session.add(product2)
    with pytest.raises(IntegrityError):
        await async_db_session.commit()
    await async_db_session.rollback()


@pytest.mark.asyncio
async def test_product_name_cannot_be_null(async_db_session: AsyncSession) -> None:
    """Verifica que el campo `name` es obligatorio."""
    product = Product(description="Refuerzo estructural", category="Construcción", price=20.00, sku="TEST001")
    async_db_session.add(product)
    with pytest.raises(IntegrityError):
        await async_db_session.commit()


@pytest.mark.asyncio
async def test_product_price_must_be_positive(async_db_session: AsyncSession) -> None:
    """Verifica que SQLAlchemy impida precios negativos o cero (requiere restricción CHECK en DB)."""
    product = Product(
        name="Producto Inválido", description="No válido", category="Prueba", price=-5.00, sku="INVALID002"
    )
    async_db_session.add(product)
    with pytest.raises(IntegrityError):
        await async_db_session.commit()
    await async_db_session.rollback()


@pytest.mark.asyncio
async def test_product_relationships(async_db_session: AsyncSession, sample_products: List[Product]) -> None:
    """(Ejemplo) Verifica que las relaciones con otras tablas funcionen correctamente."""
    product: Product = sample_products[0]
    async_db_session.add(product)
    await async_db_session.commit()
    await async_db_session.refresh(product)

    assert product.id is not None
