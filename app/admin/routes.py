import os
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, flash, jsonify
from werkzeug.utils import secure_filename
from ..models import Product
from ..timezone_config import get_naive_nigeria_time  # Use Nigeria time

admin_bp = Blueprint("admin", __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def admin_required():
    return session.get("admin")


# --------------------
# LOGIN
# --------------------
@admin_bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("password") == current_app.config["ADMIN_PASSWORD"]:
            session["admin"] = True
            return redirect(url_for("admin.dashboard"))

        flash("Invalid password.")

    return render_template("admin_login.html")


# --------------------
# DASHBOARD (Add + View)
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
            flash("Title, price and at least one image are required.")
            return redirect(url_for("admin.dashboard"))

        try:
            # Create upload directory
            upload_dir = os.path.join(current_app.root_path, "static", "uploads")
            os.makedirs(upload_dir, exist_ok=True)

            # Save main image
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                filename = f"{int(get_naive_nigeria_time().timestamp())}_{filename}"
                upload_path = os.path.join(upload_dir, filename)
                image.save(upload_path)
                main_image = f"uploads/{filename}"
            else:
                flash("Invalid main image file type.")
                return redirect(url_for("admin.dashboard"))

            # Save additional images if provided
            image_list = [main_image]
            if images:
                for img in images:
                    if img and allowed_file(img.filename):
                        filename = secure_filename(img.filename)
                        filename = f"{int(get_naive_nigeria_time().timestamp())}_{filename}"
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

            flash("Product added successfully.")
            return redirect(url_for("admin.dashboard"))

        except Exception as e:
            flash(f"Error uploading product: {str(e)}")
            return redirect(url_for("admin.dashboard"))

    products = Product.all()
    
    # Import Order here to avoid circular imports
    from ..models import Order
    orders = Order.get_all()
    
    return render_template("admin_dashboard.html", products=products, orders=orders)
@admin_bp.route("/edit/<product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    if not admin_required():
        return redirect(url_for("admin.login"))

    product = Product.get(product_id)
    if not product:
        flash("Product not found.")
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        # Only update fields that have been filled
        update_data = {}
        new_image_paths = []  # Initialize here to avoid UnboundLocalError
        
        title = request.form.get("title", "").strip()
        if title:
            update_data["title"] = title
        
        description = request.form.get("description", "").strip()
        if description:
            update_data["description"] = description
        
        price = request.form.get("price", "").strip()
        if price:
            update_data["price"] = price

        # Update product info only if there's data to update
        if update_data:
            Product.update(product_id, update_data)

        # Handle new images (independent of other updates)
        new_images = request.files.getlist("images")
        if new_images and new_images[0].filename:  # Check if files were actually selected
            upload_dir = os.path.join(current_app.root_path, "static", "uploads")
            os.makedirs(upload_dir, exist_ok=True)

            for img in new_images:
                if img and allowed_file(img.filename):
                    filename = secure_filename(img.filename)
                    filename = f"{int(get_naive_nigeria_time().timestamp())}_{filename}"
                    upload_path = os.path.join(upload_dir, filename)
                    img.save(upload_path)
                    new_image_paths.append(f"uploads/{filename}")

            if new_image_paths:
                Product.add_images(product_id, new_image_paths)

        if update_data or new_image_paths:
            flash("Product updated successfully.")
        else:
            flash("No changes made.")
        
        return redirect(url_for("admin.dashboard"))

    return render_template("admin_edit_product.html", product=product)


# --------------------
# DELETE PRODUCT IMAGE
# --------------------
@admin_bp.route("/delete-image/<product_id>/<path:image_path>")
def delete_image(product_id, image_path):
    if not admin_required():
        return redirect(url_for("admin.login"))

    Product.remove_image(product_id, image_path)
    flash("Image removed.")
    return redirect(url_for("admin.edit_product", product_id=product_id))


# --------------------
# DELETE PRODUCT
# --------------------
@admin_bp.route("/delete/<product_id>")
def delete_product(product_id):
    if not admin_required():
        return redirect(url_for("admin.login"))

    Product.delete(product_id)
    flash("Product deleted.")
    return redirect(url_for("admin.dashboard"))


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
    
    return redirect(url_for("admin.dashboard"))


# --------------------
# CLEAR WEEKLY DROP
# --------------------
@admin_bp.route("/clear")
def clear():
    if not admin_required():
        return redirect(url_for("admin.login"))

    Product.clear()
    flash("All products cleared.")
    return redirect(url_for("admin.dashboard"))


# --------------------
# LOGOUT
# --------------------
@admin_bp.route("/logout")
def logout():
    session.clear()
    flash("Logged out.")
    return redirect(url_for("admin.login"))