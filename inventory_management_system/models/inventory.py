import uuid

from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from inventory_management_system.models import Base


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), index=True, nullable=False)
    store_id = Column(UUID(as_uuid=True), index=True, nullable=False)
    quantity = Column(Integer, nullable=False)
    min_stock = Column(Integer, nullable=False)

    # 🔹 Relación con Product
    product = relationship("Product", back_populates="inventory")

    __table_args__ = (
        CheckConstraint("quantity >= 0", name="check_quantity_positive"),
        CheckConstraint("min_stock >= 0", name="check_min_stock_positive"),
    )
