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
            "sales_volume": 0
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
    def mark_pending(product_id):
        return db.products.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": {"status": "pending"}}
        )

    @staticmethod
    def clear():
        return db.products.delete_many({})
