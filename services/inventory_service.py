import json

class InventoryService:
    def __init__(self):
        with open("mock_data/inventory.json") as f:
            self.inventory = json.load(f)

    def get_all_books(self):
        return self.inventory

    def get_book(self, book_id):
        return next((b for b in self.inventory if b["id"] == book_id), None)

    def is_in_stock(self, book_id, qty):
        book = self.get_book(book_id)
        return book and book["stock"] >= qty

    def reduce_stock(self, book_id, qty):
        book = self.get_book(book_id)
        if book:
            book["stock"] -= qty
