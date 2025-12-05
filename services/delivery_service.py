import json
import uuid

class DeliveryService:
    def __init__(self):
        with open("mock_data/deliveries.json") as f:
            self.deliveries = json.load(f)

    def record_delivery(self, data):
        delivery = {
            "delivery_id": str(uuid.uuid4()),
            "order_id": data["order_id"],
            "address": data["address"],
            "status": "READY_FOR_DISPATCH"
        }
        self.deliveries.append(delivery)
        return delivery
