from locust import HttpUser, task, between

class DealershipUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def browse_homepage(self):
        self.client.get("/")

    @task(3)
    def browse_inventory(self):
        self.client.get("/inventory")

    @task(2)
    def view_car_detail(self):
        for car_id in [1, 2, 3, 4]:
            self.client.get(f"/car/{car_id}")

    @task(1)
    def submit_inquiry(self):
        self.client.post("/inquiry", data={
            "car_id": 1,
            "name": "Test Buyer",
            "phone": "0712345678",
            "email": "test@example.com",
            "inquiry_type": "general",
            "message": "Load test inquiry"
        })

    @task(1)
    def browse_api(self):
        self.client.get("/api/cars")
