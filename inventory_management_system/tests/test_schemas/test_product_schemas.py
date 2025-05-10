from uuid import uuid4

import pytest
from pydantic import ValidationError

from inventory_management_system.schemas.product import ProductCreate, ProductResponse, ProductUpdate


def test_product_create_valid():
    """Verifica que ProductCreate acepta datos válidos correctamente."""
    product_data = {
        "name": "Laptop",
        "description": "High-end gaming laptop",
        "category": "Electronics",
        "price": 1500.99,
        "sku": "LAP123",
    }
    product = ProductCreate(**product_data)
    assert product.name == "Laptop"
    assert product.description == "High-end gaming laptop"
    assert product.category == "Electronics"
    assert product.price == 1500.99
    assert product.sku == "LAP123"


def test_product_create_invalid_price():
    """Verifica que ProductCreate lanza error si el precio es menor o igual a 0."""
    with pytest.raises(ValidationError):
        ProductCreate(
            name="Tablet",
            description="Android tablet",
            category="Electronics",
            price=0,  # ❌ Precio inválido
            sku="TAB001",
        )


def test_product_create_invalid_name():
    """Verifica que ProductCreate lanza error si el nombre está vacío."""
    with pytest.raises(ValidationError):
        ProductCreate(
            name="",  # ❌ Nombre vacío
            description="A powerful smartphone",
            category="Phones",
            price=999.99,
            sku="PHN999",
        )


def test_product_update_valid():
    """Verifica que ProductUpdate acepta datos opcionales correctamente."""
    product_update = ProductUpdate(name="Updated Laptop", price=1299.99)
    assert product_update.name == "Updated Laptop"
    assert product_update.price == 1299.99
    assert product_update.description is None  # Campos opcionales no enviados


def test_product_update_invalid_price():
    """Verifica que ProductUpdate lanza error si el precio es menor o igual a 0."""
    with pytest.raises(ValidationError):
        ProductUpdate(price=-100)  # ❌ Precio inválido


def test_product_response_valid():
    """Verifica que ProductResponse maneja correctamente la conversión de datos."""
    product_data = {
        "id": uuid4(),
        "name": "Smart TV",
        "description": "4K Ultra HD Smart TV",
        "category": "Electronics",
        "price": 799.99,
        "sku": "TV4K2023",
        "stock": 25,
    }
    product = ProductResponse(**product_data)
    assert product.id == product_data["id"]
    assert product.stock == 25
    assert product.model_dump()["stock"] == 25  # Verificar serialización a diccionario
