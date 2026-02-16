from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
from ..models import Product
import urllib.parse

public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def index():
    products = Product.all()
    return render_template("index.html", products=products)


@public_bp.route("/item/<product_id>")
def item_detail(product_id):
    product = Product.get(product_id)
    if not product:
        return redirect(url_for("public.index"))
    return render_template("item_detail.html", product=product)


@public_bp.route("/order/<product_id>", methods=["POST"])
def order(product_id):
    product = Product.get(product_id)

    if not product or product["status"] != "available":
        flash("Item unavailable.")
        return redirect(url_for("public.index"))

    Product.mark_pending(product_id)

    message = f"""
🛍 NEW BONNY SELECTS ORDER

Item: {product['title']}
Price: ₦{product['price']}

Customer:
Name: {request.form.get('full_name')}
WhatsApp: {request.form.get('whatsapp')}
Location: {request.form.get('location')}

Payment: On Delivery
"""

    encoded_message = urllib.parse.quote(message)
    whatsapp_url = f"https://wa.me/{current_app.config['ADMIN_WHATSAPP']}?text={encoded_message}"

    return redirect(whatsapp_url)
