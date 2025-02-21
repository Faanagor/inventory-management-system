from models import Base
from sqlalchemy import Column, DateTime, Integer, String


class Movement(Base):
    __tablename__ = "movement"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String, index=True, nullable=False)
    source_store_id = Column(String, nullable=True)
    target_store_id = Column(String, nullable=True)
    quantity = Column(Integer, nullable=True)
    timestamp = Column(DateTime, nullable=False)
    # TO DO:
    # type = ENUM(IN, OUT, TRANSFER)
