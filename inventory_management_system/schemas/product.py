from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=5, max_length=500)
    category: str = Field(..., min_length=1, max_length=50)
    price: float = Field(..., gt=0, description="Price must be greater than 0")
    sku: str = Field(..., min_length=1)


class ProductCreate(ProductBase):
    pass  # Igual a ProductBase, pero puede extenderse si es necesario


class ProductUpdate(BaseModel):
    """Esquema para actualizar un producto. Todos los campos son opcionales."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=5, max_length=500)
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    price: Optional[float] = Field(None, gt=0, description="Price must be greater than 0")
    sku: Optional[str] = Field(None, min_length=1)


class ProductResponse(ProductBase):
    id: UUID
    stock: Optional[int] = Field(None, description="Stock total calculado desde inventory")  # 🔹 Stock opcional

    class Config:
        orm_mode = True
