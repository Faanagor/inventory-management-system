from uuid import uuid4

import pytest
from pydantic import ValidationError

from inventory_management_system.schemas.inventory import (
    InventoryCreate,
    InventoryResponse,
    InventoryTransferRequest,
    InventoryUpdate,
)


def test_inventory_create_valid():
    """Prueba la creación de un inventario válido."""
    inventory = InventoryCreate(product_id=uuid4(), store_id=uuid4(), quantity=10, min_stock=5)
    assert inventory.quantity == 10
    assert inventory.min_stock == 5


def test_inventory_create_invalid_quantity():
    """Prueba que no se pueda crear inventario si quantity < min_stock."""
    with pytest.raises(ValidationError) as excinfo:
        InventoryCreate(product_id=uuid4(), store_id=uuid4(), quantity=3, min_stock=5)  # menor que min_stock
    assert "La cantidad inicial no puede ser menor al stock mínimo." in str(excinfo.value)


def test_inventory_update_valid():
    """Prueba la actualización parcial del inventario."""
    update_data = InventoryUpdate(quantity=20)
    assert update_data.quantity == 20
    assert update_data.min_stock is None


def test_inventory_update_invalid_quantity():
    """Prueba que no se pueda actualizar con una cantidad inválida."""
    with pytest.raises(ValidationError):
        InventoryUpdate(quantity=0)  # Debe ser mayor a 0


def test_inventory_transfer_request_valid():
    """Prueba la transferencia válida de inventario."""
    transfer_request = InventoryTransferRequest(
        product_id=uuid4(), source_store_id=uuid4(), target_store_id=uuid4(), quantity=5
    )
    assert transfer_request.quantity == 5


def test_inventory_transfer_request_invalid_quantity():
    """Prueba que no se pueda transferir una cantidad menor o igual a 0."""
    with pytest.raises(ValidationError):
        InventoryTransferRequest(
            product_id=uuid4(), source_store_id=uuid4(), target_store_id=uuid4(), quantity=0  # Inválido
        )


def test_inventory_response_valid():
    """Prueba la respuesta de inventario con datos válidos."""
    response = InventoryResponse(id=uuid4(), product_id=uuid4(), store_id=uuid4(), quantity=50, min_stock=10)
    assert response.quantity == 50
    assert response.min_stock == 10
