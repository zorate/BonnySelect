from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
from ..models import Product, Order
import urllib.parse
import os
from datetime import datetime
from ..timezone_config import get_naive_nigeria_time  # Use Nigeria time

public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def index():
    products = Product.all()
    return render_template("index.html", products=products)


@public_bp.route("/item/<product_id>")
def item_detail(product_id):
    product = Product.get(product_id)
    if not product:
        flash("Product not found.")
        return redirect(url_for("public.index"))
    return render_template("item_detail.html", product=product)


@public_bp.route("/order/<product_id>", methods=["POST"])
def order(product_id):
    """
    Process order by redirecting to WhatsApp with pre-filled message.
    Order ID is generated and included in the message.
    """
    product = Product.get(product_id)

    if not product:
        flash("Product not found.")
        return redirect(url_for("public.index"))

    if product.get("status") != "available":
        flash("This item is no longer available.")
        return redirect(url_for("public.index"))

    # Get form data
    full_name = request.form.get("full_name", "").strip()
    whatsapp = request.form.get("whatsapp", "").strip()
    location = request.form.get("location", "").strip()

    if not full_name or not whatsapp or not location:
        flash("Please fill in all required fields.")
        return redirect(url_for("public.item_detail", product_id=product_id))

    # Create the order in database first to get order ID
    try:
        order_data = {
            "product_id": product_id,
            "product_title": product.get("title"),
            "product_price": product.get("price"),
            "customer_name": full_name,
            "customer_whatsapp": whatsapp,
            "delivery_location": location,
            "status": "pending"
        }
        result, order_id = Order.create(order_data)
    except Exception as e:
        flash(f"Error processing order: {str(e)}")
        return redirect(url_for("public.item_detail", product_id=product_id))

    # Create the order message with order ID
    message = f"""
🛍️ NEW BONNY SELECTS ORDER

📦 Item: {product['title']}
💰 Price: ₦{product['price']}

👤 Customer Details:
  Name: {full_name}
  WhatsApp: {whatsapp}
  Location: {location}

💳 Payment: Cash on Delivery
📅 Delivery: Saturday

🔖 ORDER ID: #{order_id}

---
Keep this order ID for your records
"""

    # Encode and redirect to WhatsApp
    encoded_message = urllib.parse.quote(message)
    whatsapp_url = f"https://wa.me/{current_app.config['ADMIN_WHATSAPP']}?text={encoded_message}"

    return redirect(whatsapp_url)