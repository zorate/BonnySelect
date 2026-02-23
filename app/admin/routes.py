import os
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, flash, jsonify, make_response
from werkzeug.utils import secure_filename
from ..models import Product, Order
from ..timezone_config import get_naive_nigeria_time
import time

admin_bp = Blueprint("admin", __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def admin_required():
    return session.get("admin")

def set_no_cache(response):
    """Add cache control headers to prevent caching"""
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0, private"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["X-Accel-Expires"] = "0"
    return response


# --------------------
# LOGIN
# --------------------
@admin_bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("password") == current_app.config["ADMIN_PASSWORD"]:
            session["admin"] = True
            response = make_response(redirect(url_for("admin.dashboard")))
            return set_no_cache(response)

        flash("Invalid password.")

    return render_template("admin_login.html")


# --------------------
# DASHBOARD (Add + View Products + View Orders)
# --------------------
@admin_bp.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if not admin_required():
        return redirect(url_for("admin.login"))

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        price = request.form.get("price")
        image = request.files.get("image")
        images = request.files.getlist("images")

        if not title or not price or not image:
            flash("❌ Title, price and at least one image are required.")
            response = make_response(redirect(url_for("admin.dashboard")))
            return set_no_cache(response)

        try:
            upload_dir = os.path.join(current_app.root_path, "static", "uploads")
            os.makedirs(upload_dir, exist_ok=True)

            # Save main image
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                filename = f"{int(time.time())}_{filename}"
                upload_path = os.path.join(upload_dir, filename)
                image.save(upload_path)
                main_image = f"uploads/{filename}"
            else:
                flash("❌ Invalid main image file type.")
                response = make_response(redirect(url_for("admin.dashboard")))
                return set_no_cache(response)

            # Save additional images
            image_list = [main_image]
            if images:
                for img in images:
                    if img and allowed_file(img.filename):
                        filename = secure_filename(img.filename)
                        filename = f"{int(time.time())}_{filename}"
                        upload_path = os.path.join(upload_dir, filename)
                        img.save(upload_path)
                        image_list.append(f"uploads/{filename}")

            # Create product
            Product.create({
                "title": title,
                "description": description,
                "price": price,
                "image": main_image,
                "images": image_list
            })

            flash("✅ Product added successfully!")
            response = make_response(redirect(url_for("admin.dashboard")))
            return set_no_cache(response)

        except Exception as e:
            flash(f"❌ Error uploading product: {str(e)}")
            response = make_response(redirect(url_for("admin.dashboard")))
            return set_no_cache(response)

    products = Product.all()
    orders = Order.get_all()
    
    response = make_response(
        render_template("admin_dashboard.html", products=products, orders=orders)
    )
    return set_no_cache(response)


@admin_bp.route("/edit/<product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    if not admin_required():
        return redirect(url_for("admin.login"))

    product = Product.get(product_id)
    if not product:
        flash("❌ Product not found.")
        response = make_response(redirect(url_for("admin.dashboard")))
        return set_no_cache(response)

    if request.method == "POST":
        update_data = {}
        new_image_paths = []
        
        title = request.form.get("title", "").strip()
        if title:
            update_data["title"] = title
        
        description = request.form.get("description", "").strip()
        if description:
            update_data["description"] = description
        
        price = request.form.get("price", "").strip()
        if price:
            update_data["price"] = price

        if update_data:
            Product.update(product_id, update_data)

        new_images = request.files.getlist("images")
        if new_images and new_images[0].filename:
            upload_dir = os.path.join(current_app.root_path, "static", "uploads")
            os.makedirs(upload_dir, exist_ok=True)

            for img in new_images:
                if img and allowed_file(img.filename):
                    filename = secure_filename(img.filename)
                    filename = f"{int(time.time())}_{filename}"
                    upload_path = os.path.join(upload_dir, filename)
                    img.save(upload_path)
                    new_image_paths.append(f"uploads/{filename}")

            if new_image_paths:
                Product.add_images(product_id, new_image_paths)

        if update_data or new_image_paths:
            flash("✅ Product updated successfully!")
        else:
            flash("⚠️ No changes made.")
        
        response = make_response(redirect(url_for("admin.dashboard")))
        return set_no_cache(response)

    return render_template("admin_edit_product.html", product=product)


# --------------------
# DELETE PRODUCT IMAGE
# --------------------
@admin_bp.route("/delete-image/<product_id>/<path:image_path>")
def delete_image(product_id, image_path):
    if not admin_required():
        return redirect(url_for("admin.login"))

    Product.remove_image(product_id, image_path)
    flash("🗑️ Image removed.")
    response = make_response(redirect(url_for("admin.edit_product", product_id=product_id)))
    return set_no_cache(response)


# --------------------
# DELETE PRODUCT
# --------------------
@admin_bp.route("/delete/<product_id>")
def delete_product(product_id):
    if not admin_required():
        return redirect(url_for("admin.login"))

    Product.delete(product_id)
    flash("🗑️ Product deleted.")
    response = make_response(redirect(url_for("admin.dashboard")))
    return set_no_cache(response)


# --------------------
# TOGGLE PRODUCT STATUS
# --------------------
@admin_bp.route("/toggle-status/<product_id>")
def toggle_status(product_id):
    if not admin_required():
        return redirect(url_for("admin.login"))

    if Product.toggle_status(product_id):
        product = Product.get(product_id)
        status_text = "✓ Available" if product.get("status") == "available" else "✓ Sold"
        flash(f"{status_text}")
    else:
        flash("❌ Error updating product status.")
    
    response = make_response(redirect(url_for("admin.dashboard")))
    return set_no_cache(response)


# --------------------
# CLEAR ALL PRODUCTS
# --------------------
@admin_bp.route("/clear")
def clear():
    if not admin_required():
        return redirect(url_for("admin.login"))

    Product.clear()
    flash("🗑️ All products cleared.")
    response = make_response(redirect(url_for("admin.dashboard")))
    return set_no_cache(response)


# --------------------
# LOGOUT
# --------------------
@admin_bp.route("/logout")
def logout():
    session.clear()
    flash("👋 Logged out.")
    response = make_response(redirect(url_for("admin.login")))
    return set_no_cache(response)


# ===============================
# ORDER STATUS MANAGEMENT
# ===============================

@admin_bp.route("/order/<order_id>/confirm", methods=["POST"])
def confirm_order(order_id):
    """Confirm an order"""
    if not admin_required():
        return redirect(url_for("admin.login"))
    
    if Order.confirm_order(order_id):
        flash("✅ Order confirmed!")
    else:
        flash("❌ Error confirming order")
    
    response = make_response(redirect(url_for("admin.dashboard")))
    return set_no_cache(response)


@admin_bp.route("/order/<order_id>/complete", methods=["POST"])
def complete_order(order_id):
    """Mark order as completed"""
    if not admin_required():
        return redirect(url_for("admin.login"))
    
    if Order.mark_completed(order_id):
        flash("✅ Order marked as completed!")
    else:
        flash("❌ Error marking order as completed")
    
    response = make_response(redirect(url_for("admin.dashboard")))
    return set_no_cache(response)


@admin_bp.route("/order/<order_id>/cancel", methods=["POST"])
def cancel_order(order_id):
    """Cancel an order"""
    if not admin_required():
        return redirect(url_for("admin.login"))
    
    if Order.cancel_order(order_id):
        flash("✅ Order cancelled!")
    else:
        flash("❌ Error cancelling order")
    
    response = make_response(redirect(url_for("admin.dashboard")))
    return set_no_cache(response)


# ===============================
# API ENDPOINTS
# ===============================

@admin_bp.route("/api/products", methods=["GET"])
def get_products_json():
    """JSON API for products - used by real-time updates"""
    if not admin_required():
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        products = Product.all()
        
        products_data = []
        for product in products:
            products_data.append({
                "_id": str(product["_id"]),
                "title": product.get("title"),
                "price": product.get("price"),
                "status": product.get("status"),
                "image": product.get("image"),
                "created_at": product.get("created_at").isoformat() if product.get("created_at") else None
            })
        
        response = make_response(jsonify(products_data))
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Content-Type"] = "application/json"
        
        return response
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500