import uuid

import pytest


@pytest.mark.asyncio
class TestProductRoutesBlackBox:
    """Pruebas de Black Box para la API de productos"""

    async def test_create_product(self, async_client, product_data):
        """Prueba la creación de un producto"""
        response = await async_client.post("api/products/", json=product_data)
        assert response.status_code == 201
        data = response.json()

        assert data["name"] == product_data["name"]
        assert data["description"] == product_data["description"]
        assert data["category"] == product_data["category"]
        assert data["price"] == product_data["price"]
        assert data["sku"] == product_data["sku"]
        assert data["stock"] == product_data["stock"]
        assert "id" in data

    async def test_get_products(self, async_client):
        """Prueba la obtención de la lista de productos"""
        response = await async_client.get("api/products/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_get_product_by_id(self, async_client, product_data):
        """Prueba la obtención de un producto por ID"""
        create_response = await async_client.post("api/products/", json=product_data)
        product_id = create_response.json()["id"]

        response = await async_client.get(f"api/products/{product_id}")
        assert response.status_code == 200
        assert response.json()["id"] == product_id

    async def test_update_product(self, async_client, product_data, product_update_data):
        """Prueba la actualización de un producto existente."""
        # Crear el producto primero
        response = await async_client.post("api/products/", json=product_data)
        assert response.status_code == 201
        created_product = response.json()
        product_id = created_product["id"]
        # Actualizar el producto con nuevos datos
        update_response = await async_client.put(f"api/products/{product_id}", json=product_update_data)
        print(f"Response Update: {update_response.json()}")  # Debugging

        assert update_response.status_code == 200
        updated_product = update_response.json()
        # Verificar que los datos hayan cambiado correctamente
        assert updated_product["name"] == product_update_data["name"]
        assert updated_product["description"] == product_update_data["description"]
        assert updated_product["category"] == product_update_data["category"]
        assert updated_product["price"] == product_update_data["price"]
        assert updated_product["sku"] == product_update_data["sku"]
        assert updated_product["stock"] == product_update_data["stock"]

    async def test_delete_product(self, async_client, product_data):
        """Prueba la eliminación de un producto"""
        create_response = await async_client.post("api/products/", json=product_data)
        product_id = create_response.json()["id"]

        response = await async_client.delete(f"api/products/{product_id}")
        assert response.status_code == 200
        assert response.json() == {"message": "Product deleted successfully"}

        # Verificar que el producto ya no existe
        response = await async_client.get(f"api/products/{product_id}")
        assert response.status_code == 404

    async def test_get_non_existent_product(self, async_client):
        """Prueba el manejo de error cuando se busca un producto inexistente"""
        non_existent_id = str(uuid.uuid4())
        response = await async_client.get(f"api/products/{non_existent_id}")
        assert response.status_code == 404
        assert response.json()["detail"] == "Product not found"

    async def test_delete_non_existent_product(self, async_client):
        """Prueba el manejo de error cuando se intenta eliminar un producto inexistente"""
        non_existent_id = str(uuid.uuid4())
        response = await async_client.delete(f"api/products/{non_existent_id}")
        assert response.status_code == 404
        assert response.json()["detail"] == "Product not found"


@pytest.mark.asyncio
class TestProductRoutesWhiteBox:
    """Pruebas de White Box enfocadas en la lógica interna"""

    async def test_create_product_invalid_data(self, async_client):
        """Prueba que no se pueda crear un producto con datos inválidos"""
        invalid_data = {
            "name": "",  # Nombre vacío
            "price": -10,  # Precio negativo
        }
        response = await async_client.post("api/products/", json=invalid_data)
        assert response.status_code == 422  # Error de validación

    async def test_update_product_invalid_data(self, async_client, product_data):
        """Prueba la validación de datos en la actualización"""
        create_response = await async_client.post("api/products/", json=product_data)
        product_id = create_response.json()["id"]

        update_data = {"price": -100}  # Precio negativo no debería permitirse
        response = await async_client.put(f"api/products/{product_id}", json=update_data)
        assert response.status_code == 422

    async def test_update_non_existent_product(self, async_client):
        """Prueba actualizar un producto que no existe"""
        non_existent_id = str(uuid.uuid4())
        update_data = {"name": "Producto Inexistente", "price": 50}
        response = await async_client.put(f"api/products/{non_existent_id}", json=update_data)
        assert response.status_code == 404
        assert response.json()["detail"] == "Product not found"
