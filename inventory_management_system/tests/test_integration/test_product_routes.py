from uuid import uuid4

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_products(async_client: AsyncClient, sample_products):
    """Prueba obtener todos los productos existentes."""
    response = await async_client.get("/api/products/")
    assert response.status_code == 200
    assert len(response.json()) == len(sample_products)


@pytest.mark.asyncio
async def test_get_product_by_id(async_client: AsyncClient, sample_products):
    """Prueba obtener un producto por ID válido e inválido."""
    valid_id = str(sample_products[0].id)
    invalid_id = str(uuid4())  # ID inexistente
    # Producto existente
    response = await async_client.get(f"/api/products/{valid_id}")
    assert response.status_code == 200
    assert response.json()["id"] == valid_id
    # Producto inexistente
    response = await async_client.get(f"/api/products/{invalid_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_product(async_client: AsyncClient):
    """Prueba crear un nuevo producto."""
    new_product = {
        "name": "Cemento Portland",
        "description": "Bolsa de cemento para construcción.",
        "category": "Construcción",
        "price": 50.00,
        "sku": "CEM123",
    }
    response = await async_client.post("/api/products/", json=new_product)
    assert response.status_code == 201
    assert response.json()["name"] == new_product["name"]
    assert response.json()["description"] == new_product["description"]
    assert response.json()["category"] == new_product["category"]
    assert response.json()["price"] == new_product["price"]
    assert response.json()["sku"] == new_product["sku"]


@pytest.mark.asyncio
async def test_update_product(async_client: AsyncClient, sample_products):
    """Prueba actualizar un producto existente."""
    product_id = str(sample_products[0].id)
    update_data = {"price": 99.99}
    response = await async_client.put(f"/api/products/{product_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["price"] == update_data["price"]


@pytest.mark.asyncio
async def test_delete_product(async_client: AsyncClient, sample_products):
    """Prueba eliminar un producto."""
    product_id = str(sample_products[0].id)
    response = await async_client.delete(f"/api/products/{product_id}")
    assert response.status_code == 200
    # Verificar que ya no existe
    response = await async_client.get(f"/api/products/{product_id}")
    assert response.status_code == 404
