from sqlalchemy.orm import DeclarativeBase


# Definir la clase base para los modelos
class Base(DeclarativeBase):
    pass


# from .inventory import Inventory
# from .movement import Movement

from .inventory import Inventory
from .movement import Movement

# Importar todos los modelos para que Alembic los detecte
from .product import Product

# Opcionalmente, puedes exponer `Base` en el namespace del módulo
__all__ = ["Base", "Product", "Inventory", "Movement"]
