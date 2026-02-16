import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change_this_in_production")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/bonny_selects")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "supersecure")
    ADMIN_WHATSAPP = os.getenv("ADMIN_WHATSAPP", "2348012345678")
    UPLOAD_FOLDER = "app/static/uploads"
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB image limit
