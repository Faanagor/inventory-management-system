import uuid

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from inventory_management_system.schemas.product import ProductCreate, ProductUpdate
from inventory_management_system.services.product_service import (
    create_product,
    delete_product,
    get_product_by_id,
    get_products,
    update_product,
)


@pytest.mark.asyncio
async def test_get_products(async_db_session: AsyncSession, sample_products):
    """Prueba la recuperación de productos con filtros y paginación."""
    products = await get_products(async_db_session, category="Construcción", limit=2)
    assert len(products) == 2
    assert all(product.category == "Construcción" for product in products)


@pytest.mark.asyncio
async def test_get_product_by_id(async_db_session: AsyncSession, sample_products):
    """Prueba la recuperación de un producto por ID."""
    product_id = sample_products[0].id
    product = await get_product_by_id(async_db_session, product_id)
    assert product.id == product_id
    assert product.name == sample_products[0].name


@pytest.mark.asyncio
async def test_get_product_by_id_not_found(async_db_session: AsyncSession):
    """Prueba el caso en que un producto no existe."""
    fake_id = uuid.uuid4()
    with pytest.raises(HTTPException) as excinfo:
        await get_product_by_id(async_db_session, fake_id)
    assert excinfo.value.status_code == 404
    assert "Producto no encontrado" in excinfo.value.detail


@pytest.mark.asyncio
async def test_create_product(async_db_session: AsyncSession):
    """Prueba la creación de un nuevo producto."""
    new_product_data = ProductCreate(
        name="Cemento Portland",
        description="Bolsa de cemento de 50 kg",
        category="Construcción",
        price=12.30,
        sku="CEMENTO001",
    )
    product = await create_product(async_db_session, new_product_data)
    assert product.id is not None
    assert product.name == new_product_data.name
    assert product.sku == new_product_data.sku


@pytest.mark.asyncio
async def test_create_product_duplicate(async_db_session: AsyncSession, sample_products):
    """Prueba la validación de productos duplicados."""
    duplicate_product_data = ProductCreate(
        name="Varilla Corrugada",  # Ya existe en sample_products
        description="Intento duplicado",
        category="Construcción",
        price=30.00,
        sku="VARILLA123",  # SKU también repetido
    )
    with pytest.raises(HTTPException) as excinfo:
        await create_product(async_db_session, duplicate_product_data)
    assert excinfo.value.status_code == 400
    assert "Ya existe un producto con este SKU o nombre" in excinfo.value.detail


@pytest.mark.asyncio
async def test_update_product(async_db_session: AsyncSession, sample_products):
    """Prueba la actualización de un producto existente."""
    product_id = sample_products[0].id
    update_data = ProductUpdate(price=29.99, description="Actualización de descripción")
    updated_product = await update_product(async_db_session, product_id, update_data)
    assert updated_product.price == 29.99
    assert updated_product.description == "Actualización de descripción"


@pytest.mark.asyncio
async def test_update_product_not_found(async_db_session: AsyncSession):
    """Prueba actualizar un producto que no existe."""
    fake_id = uuid.uuid4()
    update_data = ProductUpdate(price=29.99)
    with pytest.raises(HTTPException) as excinfo:
        await update_product(async_db_session, fake_id, update_data)
    assert excinfo.value.status_code == 404
    assert "Producto no encontrado" in excinfo.value.detail


@pytest.mark.asyncio
async def test_delete_product(async_db_session: AsyncSession, sample_products):
    """Prueba la eliminación de un producto existente."""
    product_id = sample_products[0].id
    response = await delete_product(async_db_session, product_id)
    assert response == {"message": "Producto eliminado exitosamente"}
    with pytest.raises(HTTPException) as excinfo:
        await get_product_by_id(async_db_session, product_id)
    assert excinfo.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_product_not_found(async_db_session: AsyncSession):
    """Prueba eliminar un producto que no existe."""
    fake_id = uuid.uuid4()
    with pytest.raises(HTTPException) as excinfo:
        await delete_product(async_db_session, fake_id)
    assert excinfo.value.status_code == 404
    assert "Producto no encontrado" in excinfo.value.detail
