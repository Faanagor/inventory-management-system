from locust import HttpUser, between, task


class InventoryLoadTest(HttpUser):
    wait_time = between(1, 3)  # Simula pausas entre solicitudes

    @task
    def create_inventory(self):
        data = {
            "product_id": "b0f0315e-078f-4837-8be6-6ff9e71a3ac9",
            "store_id": "b5d5b3f1-8d2e-4ef6-94e5-d5f8c5b8a9b4",
            "quantity": 23,
            "min_stock": 7,
        }
        self.client.post("/api/inventory/", json=data)

    @task
    def transfer_inventory(self):
        data = {
            "product_id": "aa81eb8b-c042-4005-9620-2020160e7fd6",
            "source_store_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "target_store_id": "9cd61e1f-f9be-4045-b67d-2cd0ffde014f",
            "quantity": 35,
        }
        self.client.post("/api/inventory/transfer/", json=data)

    @task
    def get_products(self):
        self.client.get("/api/products/")

    @task
    def post_movement(self):
        self.client.get("/api/movement/")
