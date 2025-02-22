import pytest
from fastapi import HTTPException

from inventory_management_system.schemas.product import ProductUpdate
from inventory_management_system.services.product_service import (
    create_product,
    delete_product,
    get_product_by_id,
    update_product,
)


@pytest.mark.asyncio
class TestProductService:

    async def test_create_product(self, async_session, product_create):
        """Prueba la creación de un producto válido."""
        new_product = await create_product(async_session, product_create)

        assert new_product.id is not None
        assert new_product.name == product_create.name
        assert new_product.description == product_create.description
        assert new_product.category == product_create.category
        assert new_product.price == product_create.price
        assert new_product.sku == product_create.sku
        assert new_product.stock == product_create.stock

    async def test_get_product_by_id(self, async_session, product_create):
        """Prueba obtener un producto existente."""
        new_product = await create_product(async_session, product_create)
        fetched_product = await get_product_by_id(async_session, new_product.id)

        assert fetched_product is not None
        assert fetched_product.name == product_create.name
        assert fetched_product.description == product_create.description
        assert fetched_product.category == product_create.category
        assert fetched_product.price == product_create.price
        assert fetched_product.sku == product_create.sku
        assert fetched_product.stock == product_create.stock

    async def test_get_product_by_id_not_found(self, async_session):
        """Prueba obtener un producto inexistente, esperando un error 404."""
        with pytest.raises(HTTPException) as exc_info:
            await get_product_by_id(async_session, "non_existing_id")

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Product not found"

    async def test_update_product(self, async_session, product_create, product_update):
        """Prueba la actualización de un producto en el servicio."""
        new_product = await create_product(async_session, product_create)
        new_product_updated = await update_product(async_session, new_product.id, product_update)
        await async_session.commit()
        await async_session.refresh(new_product_updated)  # Recargar datos desde la BD

        assert new_product_updated.id == new_product.id
        assert new_product_updated.name == product_update.name
        assert new_product_updated.price == product_update.price
        assert new_product_updated.description == product_update.description
        assert new_product_updated.category == product_update.category
        assert new_product_updated.sku == product_update.sku
        assert new_product_updated.stock == product_update.stock

    async def test_update_product_not_found(self, async_session):
        """Prueba actualizar un producto inexistente."""
        update_data = ProductUpdate(name="Non-Existent", price=20.0)
        with pytest.raises(HTTPException) as exc_info:
            await update_product(async_session, "fake_id", update_data)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Product not found"

    async def test_update_product_invalid_price(self, async_session, product_create):
        """Prueba actualizar un producto con precio inválido."""
        new_product = await create_product(async_session, product_create)
        update_data = ProductUpdate(price=-50)  # Precio inválido
        with pytest.raises(HTTPException) as exc_info:
            await update_product(async_session, new_product.id, update_data)

        assert exc_info.value.status_code == 422
        assert exc_info.value.detail == "Price must be greater than zero"

    async def test_delete_product(self, async_session, product_create):
        """Prueba la creación de un producto válido."""
        new_product = await create_product(async_session, product_create)
        response = await delete_product(async_session, new_product.id)
        assert response == {"message": "Product deleted successfully"}
        # Verificar que el producto ya no existe
        with pytest.raises(HTTPException) as exc_info:
            await get_product_by_id(async_session, new_product.id)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Product not found"

    async def test_delete_product_not_found(self, async_session):
        """Prueba eliminar un producto inexistente."""
        with pytest.raises(HTTPException) as exc_info:
            await delete_product(async_session, "non_existing_id")

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Product not found"
