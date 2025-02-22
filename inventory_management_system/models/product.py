import uuid

from sqlalchemy import Column, Float, Integer, String

# from sqlalchemy.orm import declarative_base
from inventory_management_system.models import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))  # UUID como string
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    category = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    sku = Column(String, nullable=False, unique=True)
    stock = Column(Integer, nullable=False, default=0)  # Se agrega stock con default 0
