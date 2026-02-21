from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from flask import current_app
from .timezone_config import get_naive_nigeria_time  # Use Nigeria time for all timestamps

db = None

def init_db(app):
    global db
    client = MongoClient(app.config["MONGO_URI"])
    db = client["convictionlog"]

class Product:

    @staticmethod
    def create(data):
        data.update({
            "status": "available",
            "created_at": get_naive_nigeria_time(),
            "updated_at": get_naive_nigeria_time(),
            "images": data.get("images", [])
        })
        return db.products.insert_one(data)

    @staticmethod
    def all():
        return list(db.products.find().sort("created_at", -1))

    @staticmethod
    def get(product_id):
        try:
            return db.products.find_one({"_id": ObjectId(product_id)})
        except:
            return None

    @staticmethod
    def delete(product_id):
        try:
            return db.products.delete_one({"_id": ObjectId(product_id)})
        except Exception:
            return None

    @staticmethod
    def update(product_id, data):
        """Update product information"""
        data['updated_at'] = get_naive_nigeria_time()
        try:
            return db.products.update_one(
                {"_id": ObjectId(product_id)},
                {"$set": data}
            )
        except Exception:
            return None

    @staticmethod
    def add_images(product_id, image_paths):
        """Add multiple images to a product"""
        try:
            return db.products.update_one(
                {"_id": ObjectId(product_id)},
                {
                    "$push": {"images": {"$each": image_paths}},
                    "$set": {"updated_at": get_naive_nigeria_time()}
                }
            )
        except Exception:
            return None

    @staticmethod
    def remove_image(product_id, image_path):
        """Remove a specific image from product"""
        try:
            return db.products.update_one(
                {"_id": ObjectId(product_id)},
                {
                    "$pull": {"images": image_path},
                    "$set": {"updated_at": get_naive_nigeria_time()}
                }
            )
        except Exception:
            return None

    @staticmethod
    def toggle_status(product_id):
        """
        Toggle product status between available and sold.
        Admin controls when product is actually sold via admin dashboard.
        """
        product = Product.get(product_id)
        if not product:
            return False
        
        new_status = "sold" if product.get("status") == "available" else "available"
        
        try:
            return db.products.update_one(
                {"_id": ObjectId(product_id)},
                {"$set": {"status": new_status, "updated_at": get_naive_nigeria_time()}}
            ).modified_count > 0
        except Exception:
            return False

    @staticmethod
    def clear():
        return db.products.delete_many({})


class Order:
    """Order management class"""

    @staticmethod
    def _generate_order_id():
        """Generate a random 5-digit order ID"""
        import random
        while True:
            order_id = random.randint(10000, 99999)
            # Ensure uniqueness
            if not db.orders.find_one({"order_id": order_id}):
                return order_id

    @staticmethod
    def create(data):
        """Create a new order with 5-digit order ID"""
        order_id = Order._generate_order_id()
        data.update({
            "order_id": order_id,
            "created_at": get_naive_nigeria_time(),
            "status": "pending"
        })
        result = db.orders.insert_one(data)
        return result, order_id

    @staticmethod
    def get(order_id):
        """Get order by MongoDB ID"""
        try:
            return db.orders.find_one({"_id": ObjectId(order_id)})
        except Exception:
            return None

    @staticmethod
    def get_by_order_id(order_id):
        """Get order by 5-digit order ID"""
        try:
            return db.orders.find_one({"order_id": order_id})
        except Exception:
            return None

    @staticmethod
    def get_all():
        """Get all orders sorted by date (newest first)"""
        return list(db.orders.find().sort("created_at", -1))


    @staticmethod
    def confirm_order(order_id):
        """Mark order as confirmed (admin confirms they have the item)"""
        try:
            return db.orders.update_one(
                {"_id": ObjectId(order_id)},
                {"$set": {
                    "status": "confirmed",
                    "confirmed_at": get_naive_nigeria_time(),
                    "updated_at": get_naive_nigeria_time()
                }}
            ).modified_count > 0
        except Exception:
            return False

    @staticmethod
    def mark_completed(order_id):
        """Mark order as completed (delivered on Saturday)"""
        try:
            return db.orders.update_one(
                {"_id": ObjectId(order_id)},
                {"$set": {
                    "status": "completed",
                    "completed_at": get_naive_nigeria_time(),
                    "updated_at": get_naive_nigeria_time()
                }}
            ).modified_count > 0
        except Exception:
            return False

    @staticmethod
    def cancel_order(order_id):
        """Mark order as cancelled (customer changed mind)"""
        try:
            return db.orders.update_one(
                {"_id": ObjectId(order_id)},
                {"$set": {
                    "status": "cancelled",
                    "cancelled_at": get_naive_nigeria_time(),
                    "updated_at": get_naive_nigeria_time()
                }}
            ).modified_count > 0
        except Exception:
            return False

    @staticmethod
    def update_status(order_id, status):
        """Update order status - generic method"""
        try:
            return db.orders.update_one(
                {"_id": ObjectId(order_id)},
                {"$set": {"status": status, "updated_at": get_naive_nigeria_time()}}
            ).modified_count > 0
        except Exception:
            return False

    @staticmethod
    def delete(order_id):
        """Delete an order"""
        try:
            return db.orders.delete_one({"_id": ObjectId(order_id)})
        except Exception:
            return None