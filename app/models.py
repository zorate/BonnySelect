from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from flask import current_app

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
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "sales_volume": 0,
            "images": data.get("images", [])  # Support for multiple images
        })
        return db.products.insert_one(data)

    @staticmethod
    def all():
        return list(db.products.find().sort("created_at", -1))

    @staticmethod
    def get(product_id):
        return db.products.find_one({"_id": ObjectId(product_id)})

    @staticmethod
    def delete(product_id):
        try:
            return db.products.delete_one({"_id": ObjectId(product_id)})
        except Exception:
            return None

    @staticmethod
    def update(product_id, data):
        """Update product information"""
        data['updated_at'] = datetime.utcnow()
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
                    "$set": {"updated_at": datetime.utcnow()}
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
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
        except Exception:
            return None

    @staticmethod
    def mark_pending(product_id):
        return db.products.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": {"status": "pending", "updated_at": datetime.utcnow()}}
        )

    @staticmethod
    def mark_sold(product_id):
        """Mark product as sold"""
        return db.products.update_one(
            {"_id": ObjectId(product_id)},
            {
                "$set": {"status": "sold", "updated_at": datetime.utcnow()},
                "$inc": {"sales_volume": 1}
            }
        )

    @staticmethod
    def clear():
        return db.products.delete_many({})