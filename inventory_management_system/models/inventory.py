from models import Base
from sqlalchemy import Column, Integer, String


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String, index=True, nullable=False)
    store_id = Column(String, nullable=True)
    quantity = Column(Integer, nullable=True)
    min_stock = Column(Integer, nullable=False)
