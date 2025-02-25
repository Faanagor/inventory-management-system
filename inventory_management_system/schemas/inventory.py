from typing import Optional, Type
from uuid import UUID

from pydantic import BaseModel, Field, ValidationInfo, field_validator


class InventoryBase(BaseModel):
    product_id: UUID = Field(..., description="ID del producto en el inventario")
    store_id: UUID = Field(..., description="ID de la tienda que contiene el producto")
    quantity: int = Field(..., gt=0, description="Cantidad inicial en stock (mayor a 0)")
    min_stock: int = Field(..., gt=0, description="Mínimo de stock antes de alerta")


class InventoryCreate(InventoryBase):
    """Esquema usado para crear un nuevo inventario."""

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls: Type["InventoryCreate"], value: int, info: ValidationInfo) -> int:
        """Valida que la cantidad inicial no sea menor al stock mínimo."""
        min_stock = info.data.get("min_stock")  # Acceder al min_stock validado
        if min_stock is not None and value < min_stock:
            raise ValueError("La cantidad inicial no puede ser menor al stock mínimo.")
        return value


class InventoryUpdate(BaseModel):
    """Esquema para actualizar parcialmente el inventario."""

    quantity: Optional[int] = Field(None, gt=0, description="Nueva cantidad en stock")
    min_stock: Optional[int] = Field(None, gt=0, description="Nuevo mínimo de stock antes de alerta")


class InventoryTransferRequest(BaseModel):
    """Esquema para la transferencia de inventario entre tiendas."""

    product_id: UUID = Field(..., description="ID del producto a transferir")
    source_store_id: UUID = Field(..., description="ID de la tienda de origen")
    target_store_id: UUID = Field(..., description="ID de la tienda de destino")
    quantity: int = Field(..., gt=0, description="Cantidad a transferir (debe ser mayor a 0)")


class InventoryResponse(InventoryBase):
    """Esquema para responder con datos de inventario existentes."""

    id: UUID = Field(..., description="ID único del inventario")

    class Config:
        orm_mode = True  # Permite convertir SQLAlchemy a Pydantic automáticamente
