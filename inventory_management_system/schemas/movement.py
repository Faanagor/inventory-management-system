import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class MovementBase(BaseModel):
    product_id: str = Field(..., min_length=1, max_length=100)
    source_store_id: Optional[str]
    target_store_id: Optional[str]
    quantity: int = Field(..., gt=0)  # No puede ser negativo
    type: str = Field(..., min_length=1)


class MovementResponse(MovementBase):
    id: UUID
    timestamp: datetime.datetime
