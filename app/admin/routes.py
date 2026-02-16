import os
from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, flash
from werkzeug.utils import secure_filename
from ..models import Product

admin_bp = Blueprint("admin", __name__)


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

        if not title or not price or not image:
            flash("Title, price and image are required.")
            return redirect(url_for("admin.dashboard"))

        filename = secure_filename(image.filename)

        upload_dir = os.path.join(current_app.root_path, "static", "uploads")
        os.makedirs(upload_dir, exist_ok=True)

        upload_path = os.path.join(upload_dir, filename)
        image.save(upload_path)

        Product.create({
            "title": title,
            "description": description,
            "price": price,
            "image": f"uploads/{filename}"
        })

        flash("Product added.")
        return redirect(url_for("admin.dashboard"))

    products = Product.all()
    return render_template("admin_dashboard.html", products=products)


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
# CLEAR WEEKLY DROP
# --------------------
@admin_bp.route("/clear")
def clear():
    if not admin_required():
        return redirect(url_for("admin.login"))

    Product.clear()
    flash("Drop cleared.")
    return redirect(url_for("admin.dashboard"))
