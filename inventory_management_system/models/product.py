from sqlalchemy import Column, Float, Integer, String

from inventory_management_system.models import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    category = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    sku = Column(String, nullable=False)
    # new_field = Column(String, nullable=False)
