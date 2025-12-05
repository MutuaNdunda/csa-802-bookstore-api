import json
import uuid

class SalesService:
    def __init__(self):
        with open("mock_data/sales.json") as f:
            self.sales = json.load(f)

    def create_order(self, book_id, qty, customer):
        order = {
            "order_id": str(uuid.uuid4()),
            "book_id": book_id,
            "quantity": qty,
            "customer": customer,
            "status": "PAID"
        }
        self.sales.append(order)
        return order
