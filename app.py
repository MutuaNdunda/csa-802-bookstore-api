from flask import Flask, request, jsonify, redirect
from functools import wraps
from flasgger import Swagger
from dotenv import load_dotenv
import os

# Mock services
from services.inventory_service import InventoryService
from services.sales_service import SalesService
from services.delivery_service import DeliveryService

# ---------------------------------------------------------
# APP INITIALIZATION
# ---------------------------------------------------------
app = Flask(__name__)

# Swagger configuration with API Key support
swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Bookstore Integration API",
        "description": "API for Inventory, Sales, and Delivery Systems",
        "version": "1.0.0"
    },
    "securityDefinitions": {
        "ApiKeyAuth": {
            "type": "apiKey",
            "name": "x-api-key",
            "in": "header"
        }
    },
    "security": [{"ApiKeyAuth": []}]
}

swagger = Swagger(app, template=swagger_template)

# Load API KEY
load_dotenv()
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY environment variable is not set")

# ---------------------------------------------------------
# API KEY AUTH DECORATOR
# ---------------------------------------------------------
def require_api_key(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        key = request.headers.get("x-api-key")
        if key != API_KEY:
            return jsonify({"error": "Unauthorized - Invalid API Key"}), 401
        return func(*args, **kwargs)
    return wrapper

# ---------------------------------------------------------
# INITIALIZE SERVICES
# ---------------------------------------------------------
inventory = InventoryService()
sales = SalesService()
delivery = DeliveryService()

# ---------------------------------------------------------
# INVENTORY ENDPOINTS
# ---------------------------------------------------------
@app.route("/api/books", methods=["GET"])
@require_api_key
def get_all_books():
    """
    Get all available books.
    ---
    tags:
      - Inventory
    security:
      - ApiKeyAuth: []
    responses:
      200:
        description: A list of books
    """
    return jsonify(inventory.get_all_books()), 200


@app.route("/api/books/<book_id>", methods=["GET"])
@require_api_key
def get_book_details(book_id):
    """
    Get a book's details by ID.
    ---
    tags:
      - Inventory
    security:
      - ApiKeyAuth: []
    parameters:
      - name: book_id
        in: path
        type: string
        required: true
        description: Book ID
    responses:
      200:
        description: Book details
      404:
        description: Book not found
    """
    book = inventory.get_book(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(book), 200

# ---------------------------------------------------------
# SALES ENDPOINTS
# ---------------------------------------------------------
@app.route("/api/orders", methods=["POST"])
@require_api_key
def place_order():
    """
    Place a new order.
    ---
    tags:
      - Sales
    security:
      - ApiKeyAuth: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          id: Order
          required:
            - book_id
            - quantity
            - customer
          properties:
            book_id:
              type: string
            quantity:
              type: integer
            customer:
              type: string
    responses:
      201:
        description: Order created
      400:
        description: Invalid request
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON body is required"}), 400

    book_id = data.get("book_id")
    quantity = data.get("quantity")
    customer = data.get("customer")

    if not all([book_id, quantity, customer]):
        return jsonify({"error": "Missing fields: book_id, quantity, customer"}), 400

    if not inventory.is_in_stock(book_id, quantity):
        return jsonify({"error": "Insufficient stock"}), 400

    order = sales.create_order(book_id, quantity, customer)
    inventory.reduce_stock(book_id, quantity)

    return jsonify(order), 201

# ---------------------------------------------------------
# DELIVERY ENDPOINTS
# ---------------------------------------------------------
@app.route("/api/delivery/update", methods=["POST"])
@require_api_key
def update_delivery():
    """
    Update delivery information.
    ---
    tags:
      - Delivery
    security:
      - ApiKeyAuth: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          id: Delivery
          required:
            - order_id
            - address
          properties:
            order_id:
              type: string
            address:
              type: string
    responses:
      201:
        description: Delivery updated
      400:
        description: Missing fields
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON body is required"}), 400

    order_id = data.get("order_id")
    address = data.get("address")

    if not order_id or not address:
        return jsonify({"error": "Missing fields: order_id, address"}), 400

    update = delivery.record_delivery(data)

    return jsonify(update), 201

# ---------------------------------------------------------
# HOME ROUTE
# ---------------------------------------------------------
@app.route("/")
def home():
    """
    API Home
    ---
    tags:
      - Home
    responses:
      200:
        description: API status
    """
    return jsonify({"message": "Bookstore Integration API Running"})


# ---------------------------------------------------------
# START APP (LOCAL USE ONLY)
# ---------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
