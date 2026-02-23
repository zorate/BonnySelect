import os
import json
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from ..models import Product, Order
from ..timezone_config import get_naive_nigeria_time

public_bp = Blueprint("public", __name__)

# ===============================
# MARKETPLACE
# ===============================

@public_bp.route("/")
def index():
    """Homepage - marketplace with cart"""
    products = Product.all()
    return render_template("index.html", products=products)


@public_bp.route("/product/<product_id>")
def item_detail(product_id):
    """Product detail page"""
    product = Product.get(product_id)
    if not product:
        flash("Product not found.")
        return redirect(url_for("public.index"))
    
    return render_template("public/item_detail.html", product=product)


# ===============================
# SINGLE ITEM ORDER (Direct from detail page)
# ===============================

@public_bp.route("/product/<product_id>/order", methods=["POST"])
def order(product_id):
    """Order a single item directly from product detail page"""
    product = Product.get(product_id)
    if not product:
        flash("Product not found.")
        return redirect(url_for("public.index"))

    full_name = request.form.get("full_name")
    whatsapp = request.form.get("whatsapp")
    location = request.form.get("location")

    if not all([full_name, whatsapp, location]):
        flash("All fields are required.")
        return redirect(url_for("public.item_detail", product_id=product_id))

    # Create order with single item in items array
    order_data = {
        "customer_name": full_name,
        "customer_whatsapp": whatsapp,
        "delivery_location": location,
        "items": [
            {
                "product_id": str(product["_id"]),
                "product_title": product["title"],
                "quantity": 1,
                "price": product["price"]
            }
        ],
        "total_price": int(product["price"])
    }

    result, order_id = Order.create(order_data)

    if result:
        # Generate WhatsApp message
        whatsapp_msg = Order.generate_whatsapp_message(order_id, order_data)
        flash(f"✅ Order #{order_id} created!")
        return redirect(whatsapp_msg)
    else:
        flash("Error creating order.")
        return redirect(url_for("public.item_detail", product_id=product_id))


# ===============================
# SHOPPING CART CHECKOUT
# ===============================

@public_bp.route("/checkout")
def checkout():
    """Checkout page for multiple items"""
    return render_template("public/checkout.html")


@public_bp.route("/place-order", methods=["POST"])
def place_order():
    """Process multi-item order from shopping cart"""
    full_name = request.form.get("full_name")
    whatsapp = request.form.get("whatsapp")
    location = request.form.get("location")

    if not all([full_name, whatsapp, location]):
        flash("All fields are required.")
        return redirect(url_for("public.checkout"))

    try:
        cart_items_str = request.form.get("cart_items", "[]")
        cart_items = json.loads(cart_items_str)
        
        if not cart_items:
            flash("Cart is empty.")
            return redirect(url_for("public.checkout"))

        # Calculate total price
        total_price = sum(int(item.get('price', 0)) * item.get('quantity', 1) for item in cart_items)

        # Prepare order data with items array
        order_data = {
            "customer_name": full_name,
            "customer_whatsapp": whatsapp,
            "delivery_location": location,
            "items": [
                {
                    "product_id": item.get('_id', ''),
                    "product_title": item.get('title', 'Product'),
                    "quantity": item.get('quantity', 1),
                    "price": item.get('price', '0')
                }
                for item in cart_items
            ],
            "total_price": total_price
        }

        # Create order in database
        result, order_id = Order.create(order_data)

        if result:
            # Generate WhatsApp message
            whatsapp_msg = Order.generate_whatsapp_message(order_id, order_data)
            flash(f"✅ Order #{order_id} placed successfully!")
            return redirect(whatsapp_msg)
        else:
            flash("Error creating order.")
            return redirect(url_for("public.checkout"))

    except json.JSONDecodeError as e:
        flash("Invalid cart data.")
        return redirect(url_for("public.checkout"))
    except Exception as e:
        flash(f"Error: {str(e)}")
        return redirect(url_for("public.checkout"))