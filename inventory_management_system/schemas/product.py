from typing import Optional

from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    price: float
    stock: int
    category: str


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    category: Optional[str] = None
