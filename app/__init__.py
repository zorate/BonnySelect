import os
from flask import Flask, send_from_directory
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

    # Serve manifest.json from static folder
    @app.route('/manifest.json')
    def manifest():
        return send_from_directory(os.path.join(app.root_path, 'static'), 'manifest.json')

    # Serve service worker from static folder
    @app.route('/sw.js')
    def service_worker():
        response = send_from_directory(os.path.join(app.root_path, 'static'), 'sw.js')
        response.headers['Content-Type'] = 'application/javascript'
        response.headers['Cache-Control'] = 'no-cache'
        return response

    # Serve app icons from static folder
    @app.route('/static/icons/<path:filename>')
    def serve_icons(filename):
        return send_from_directory(os.path.join(app.root_path, 'static', 'icons'), filename)

    return app