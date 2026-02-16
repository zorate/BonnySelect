import os
from flask import Flask
from .config import Config
from .models import init_db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize MongoDB
    init_db(app)

    # Register blueprints
    from .public.routes import public_bp
    from .admin.routes import admin_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")

    return app
