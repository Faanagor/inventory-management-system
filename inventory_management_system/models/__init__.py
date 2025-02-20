from sqlalchemy.orm import declarative_base

Base = declarative_base()

from inventory_management_system.models import inventory, movement, product
