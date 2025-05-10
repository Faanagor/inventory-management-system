from datetime import datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from inventory_management_system.schemas.movement import MovementCreate, MovementType


def test_movement_create_valid_in():
    """Debe permitir la creación de un movimiento tipo IN con target_store_id."""
    movement = MovementCreate(
        product_id=uuid4(),
        target_store_id=uuid4(),
        quantity=10,
        type=MovementType.IN,
    )
    assert movement.type == MovementType.IN
    assert isinstance(movement.timestamp, datetime)


def test_movement_create_invalid_in():
    """Debe fallar si intentamos crear un movimiento tipo IN sin target_store_id."""
    with pytest.raises(ValidationError) as excinfo:
        MovementCreate(
            product_id=uuid4(),
            quantity=10,
            type=MovementType.IN,
        )
    assert "target_store_id es obligatorio para movimientos IN" in str(excinfo.value)


def test_movement_create_valid_out():
    """Debe permitir la creación de un movimiento tipo OUT con source_store_id."""
    movement = MovementCreate(
        product_id=uuid4(),
        source_store_id=uuid4(),
        quantity=5,
        type=MovementType.OUT,
    )
    assert movement.type == MovementType.OUT
    assert isinstance(movement.timestamp, datetime)


def test_movement_create_invalid_out():
    """Debe fallar si intentamos crear un movimiento tipo OUT sin source_store_id."""
    with pytest.raises(ValidationError) as excinfo:
        MovementCreate(
            product_id=uuid4(),
            quantity=5,
            type=MovementType.OUT,
        )
    assert "source_store_id es obligatorio para movimientos OUT" in str(excinfo.value)


def test_movement_create_valid_transfer():
    """Debe permitir la creación de un movimiento tipo TRANSFER con source_store_id y target_store_id."""
    movement = MovementCreate(
        product_id=uuid4(),
        source_store_id=uuid4(),
        target_store_id=uuid4(),
        quantity=3,
        type=MovementType.TRANSFER,
    )
    assert movement.type == MovementType.TRANSFER
    assert isinstance(movement.timestamp, datetime)


def test_movement_create_invalid_transfer():
    """Debe fallar si intentamos crear un movimiento tipo TRANSFER sin source_store_id o target_store_id."""
    with pytest.raises(ValidationError) as excinfo:
        MovementCreate(
            product_id=uuid4(),
            source_store_id=uuid4(),
            quantity=3,
            type=MovementType.TRANSFER,
        )
    assert "source_store_id y target_store_id son obligatorios para movimientos TRANSFER" in str(excinfo.value)
