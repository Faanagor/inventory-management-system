import enum
import uuid

from sqlalchemy import CheckConstraint, Column, DateTime, Enum, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func

from inventory_management_system.models import Base


class MovementType(str, enum.Enum):
    IN = "IN"
    OUT = "OUT"
    TRANSFER = "TRANSFER"


class Movement(Base):
    __tablename__ = "movements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    source_store_id = Column(UUID(as_uuid=True), nullable=True)
    target_store_id = Column(UUID(as_uuid=True), nullable=True)
    quantity = Column(Integer, nullable=False)
    timestamp = Column(DateTime, server_default=func.now(), nullable=False)
    type = Column(Enum(MovementType), nullable=False)

    product = relationship("Product", back_populates="movements")

    __table_args__ = (CheckConstraint("quantity > 0", name="check_quantity_positive"),)

    @validates("type")
    def validate_type(self, key, value):
        if value not in MovementType.__members__.values():
            raise ValueError(f"Invalid movement type: {value}")
        return value
