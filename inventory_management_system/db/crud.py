from db.models import Product
from schemas.product import ProductCreate, ProductUpdate
from sqlalchemy.orm import Session


def get_products(
    db: Session,
    category: str = None,
    price: float = None,
    page: int = 1,
    limit: int = 10,
):
    query = db.query(Product)
    if category:
        query = query.filter(Product.category == category)
    if price:
        query = query.filter(Product.price <= price)
    return query.offset((page - 1) * limit).limit(limit).all()


def get_product_by_id(db: Session, id: int):
    return db.query(Product).filter(Product.id == id).first()


def create_product(db: Session, product: ProductCreate) -> Product:
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(db: Session, id: int, product: ProductUpdate):
    db_product = db.query(Product).filter(Product.id == id).first()
    if db_product:
        for key, value in product.dict(exclude_unset=True).items():
            setattr(db_product, key, value)
        db.commit()
        db.refresh(db_product)
        return db_product
    return None


def delete_product(db: Session, id: int):
    db_product = db.query(Product).filter(Product.id == id).first()
    if db_product:
        db.delete(db_product)
        db.commit()
        return {"message": "Product deleted successfully"}
    return {"message": "Product not found"}
