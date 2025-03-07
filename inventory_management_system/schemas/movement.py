from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional, Type
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class MovementType(str, Enum):
    IN = "IN"
    OUT = "OUT"
    TRANSFER = "TRANSFER"


class MovementBase(BaseModel):
    product_id: UUID = Field(..., description="ID del producto en los movimientos")
    source_store_id: Optional[UUID] = Field(None, description="ID de la tienda que contiene el producto")
    target_store_id: Optional[UUID] = Field(None, description="ID de la tienda hacia donde va el producto")
    quantity: int = Field(..., gt=0, description="Cantidad del producto en el movimiento (mayor a 0)")
    # timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    type: MovementType


class MovementCreate(MovementBase):
    @model_validator(mode="before")
    @classmethod
    def validate_stores(cls: Type["MovementCreate"], values: dict[str, Any]) -> dict[str, Any]:
        # Validar y corregir el timestamp si viene vacío
        if "timestamp" in values and values["timestamp"] in ("", None):
            values["timestamp"] = datetime.now(timezone.utc)
        movement_type: MovementType = values.get("type")
        source_store: Optional[UUID] = values.get("source_store_id")
        target_store: Optional[UUID] = values.get("target_store_id")
        if movement_type == MovementType.IN and target_store is None:
            raise ValueError("target_store_id es obligatorio para movimientos IN")
        if movement_type == MovementType.OUT and source_store is None:
            raise ValueError("source_store_id es obligatorio para movimientos OUT")
        if movement_type == MovementType.TRANSFER and (source_store is None or target_store is None):
            raise ValueError("source_store_id y target_store_id son obligatorios para movimientos TRANSFER")
        return values


class MovementResponse(MovementBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)
