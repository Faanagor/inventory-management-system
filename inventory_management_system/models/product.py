import uuid

from sqlalchemy import Column, Float, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from inventory_management_system.models import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=False)
    category = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    sku = Column(String, nullable=False, unique=True)

    # 🔹 Relación con Inventory (stock ahora se maneja desde inventory)
    inventory = relationship("Inventory", back_populates="product", cascade="all, delete-orphan")
