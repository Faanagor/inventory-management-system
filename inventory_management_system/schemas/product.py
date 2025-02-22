from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = None
    price: float = Field(..., gt=0)  # El precio debe ser mayor a 0
    sku: str = Field(..., min_length=1)
    stock: int = Field(..., ge=0)  # No puede ser negativo


class ProductCreate(ProductBase):
    pass  # Igual a ProductBase, pero puede extenderse si es necesario


class ProductUpdate(ProductBase):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    sku: Optional[str] = None
    stock: Optional[int] = None


class ProductResponse(BaseModel):
    id: UUID
    name: str
    description: str
    category: str
    price: float = Field(gt=0, description="Price must be great than or equal to 0")
    sku: str
    stock: int = Field(gt=0, description="Stock must be great than or equal to 0")
