import os
from datetime import datetime
from flask import current_app
from bson.objectid import ObjectId
from .timezone_config import get_naive_nigeria_time
import time

db = None

def init_db(app):
    global db
    from pymongo import MongoClient
    client = MongoClient(app.config["MONGO_URI"])
    db = client["convictionlog"]

# ===============================
# PRODUCT MODEL
# ===============================

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
            ).modified_count > 0
        except Exception:
            return False

    @staticmethod
    def toggle_status(product_id):
        """Toggle between available and sold"""
        try:
            product = Product.get(product_id)
            if not product:
                return False
            
            new_status = "sold" if product["status"] == "available" else "available"
            return Product.update(product_id, {"status": new_status})
        except Exception:
            return False

    @staticmethod
    def add_images(product_id, image_paths):
        """Add multiple images to a product"""
        try:
            return db.products.update_one(
                {"_id": ObjectId(product_id)},
                {"$push": {"images": {"$each": image_paths}}}
            ).modified_count > 0
        except Exception:
            return False

    @staticmethod
    def remove_image(product_id, image_path):
        """Remove an image from product"""
        try:
            return db.products.update_one(
                {"_id": ObjectId(product_id)},
                {"$pull": {"images": image_path}}
            ).modified_count > 0
        except Exception:
            return False

    @staticmethod
    def clear():
        return db.products.delete_many({})


# ===============================
# ORDER MODEL - COMPLETE REWRITE
# ===============================

class Order:
    """Order management with support for single and multiple items"""

    @staticmethod
    def _generate_order_id():
        """Generate a random 5-digit order ID"""
        import random
        while True:
            order_id = random.randint(10000, 99999)
            if not db.orders.find_one({"order_id": order_id}):
                return order_id

    @staticmethod
    def create(data):
        """Create a new order with single or multiple items"""
        order_id = Order._generate_order_id()
        data.update({
            "order_id": order_id,
            "created_at": get_naive_nigeria_time(),
            "status": "pending",
            "items": data.get("items", []),  # Always store as items array
            "total_price": data.get("total_price", 0)
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
    def get_by_product(product_id):
        """Get all orders containing a specific product"""
        return list(db.orders.find({"items.product_id": product_id}).sort("created_at", -1))

    @staticmethod
    def confirm_order(order_id):
        """Mark order as confirmed"""
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
        """Mark order as completed (delivered)"""
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
        """Mark order as cancelled"""
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

    @staticmethod
    def generate_whatsapp_message(order_id, order_data):
        """Generate WhatsApp message for single or multiple items"""
        from urllib.parse import quote
        from flask import current_app
        
        customer_name = order_data.get("customer_name", "Customer")
        customer_whatsapp = order_data.get("customer_whatsapp", "")
        delivery_location = order_data.get("delivery_location", "")
        items = order_data.get("items", [])
        total_price = order_data.get("total_price", 0)

        # Start message
        message = f"*Bonny Selects Order #{order_id}*\n\n"
        message += f"Hi {customer_name}! 👋\n\n"
        message += f"Thank you for your order!\n\n"

        # List items
        if len(items) == 1:
            # Single item
            item = items[0]
            message += f"*Item:*\n"
            message += f"{item.get('product_title', 'Product')}\n"
            message += f"Qty: {item.get('quantity', 1)}\n"
            message += f"Price: ₦{item.get('price', 0)}\n\n"
        else:
            # Multiple items
            message += f"*Your Items ({len(items)}):*\n"
            for i, item in enumerate(items, 1):
                product_title = item.get("product_title", "Product")
                quantity = item.get("quantity", 1)
                price = item.get("price", 0)
                item_total = int(price) * quantity
                
                message += f"{i}. {product_title}\n"
                message += f"   Qty: {quantity} × ₦{price} = ₦{item_total:,}\n"
            message += "\n"

        message += f"*Total: ₦{total_price:,}*\n\n"

        # Order details
        message += "*Delivery Details:*\n"
        message += f"📍 Location: {delivery_location}\n"
        message += f"📱 Phone: {customer_whatsapp}\n"
        message += f"📅 Delivery: Saturday\n"
        message += f"💳 Payment: On Delivery\n\n"

        # Call to action
        message += "✓ Please confirm your order by replying to this message.\n"
        message += "Thanks for choosing Bonny Selects! 🙌\n\n"
        message += "*#BonnySelects #PremiumJerseys*"

        # URL encode
        encoded_message = quote(message)
        
        # Get admin WhatsApp from config
        admin_whatsapp = current_app.config.get("ADMIN_WHATSAPP", "2349012345678")
        
        whatsapp_url = f"https://wa.me/{admin_whatsapp}?text={encoded_message}"
        
        return whatsapp_url