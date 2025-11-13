import os
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)

DATA_FILE = "orders.json"

# -------- MENU DEFINITION WITH CATEGORIES --------
MENU_CATEGORIES = [
    {
        "id": "sabzi",
        "name": "Sabzi",
        "items": [
            {"id": 1,  "name": "Aloo Palak"},
            {"id": 2,  "name": "Aloo Mutter"},
            {"id": 3,  "name": "Kari Pakoda"},
            {"id": 4,  "name": "Baigan Bharta"},
            {"id": 5,  "name": "Dal Makhani"},
            {"id": 6,  "name": "Dal Arhar Butter Fry"},
            {"id": 7,  "name": "Punjabi Dal Tadka"},
            {"id": 8,  "name": "Palak Mutter"},
            {"id": 9,  "name": "Aloo Gobhi"},
            {"id": 10, "name": "Aloo Jeera"},
            {"id": 11, "name": "Rajma"},
            {"id": 12, "name": "Mix Vegetable"},
            {"id": 13, "name": "Baigan Bharta Mutter"},
            {"id": 14, "name": "Mutter Masala"},
            {"id": 15, "name": "Khoya Mutter"},
            {"id": 16, "name": "Dum Aloo Special"},
            {"id": 17, "name": "Mutter Mushroom"},
            {"id": 18, "name": "Mushroom Masala"},
            {"id": 19, "name": "Kadai Chaap"},
            {"id": 20, "name": "Malai Chaap"},
            {"id": 21, "name": "Chaap Masala"},
            {"id": 22, "name": "Keema Chaap"},
        ],
    },

    {
        "id": "paneer_special",
        "name": "Paneer Special",
        "items": [
            {"id": 101, "name": "Sahi Paneer"},
            {"id": 102, "name": "Paneer Tomato"},
            {"id": 103, "name": "Paneer Masala"},
            {"id": 104, "name": "Paneer Bhurji"},
            {"id": 105, "name": "Khoya Paneer"},
            {"id": 106, "name": "Paneer Mutter Masala"},
            {"id": 107, "name": "Mutter Paneer"},
            {"id": 108, "name": "Palak Paneer"},
            {"id": 109, "name": "Malai Kofta"},
            {"id": 110, "name": "Paneer Do Piyaza"},
            {"id": 111, "name": "Paneer Labdar"},
            {"id": 112, "name": "Kadai Paneer"},
            {"id": 113, "name": "Paneer Butter Masala"},
            {"id": 114, "name": "Stuff Tomato"},
        ],
    },

    {
        "id": "raita_salad",
        "name": "Raita & Salad",
        "items": [
            {"id": 201, "name": "Mix Raita"},
            {"id": 202, "name": "Dahi"},
            {"id": 203, "name": "Raita Bundi"},
            {"id": 204, "name": "Family Green Salad"},
            {"id": 205, "name": "Green Salad Small"},
            {"id": 206, "name": "Papad"},
            {"id": 207, "name": "Papad Fry"},
            {"id": 208, "name": "Masala Papad"},
        ],
    },

    {
        "id": "basmati_ka_khajana",
        "name": "Basmati Ka Khajana",
        "items": [
            {"id": 301, "name": "Sada Rice"},
            {"id": 302, "name": "Jeera Rice"},
            {"id": 303, "name": "Fry Rice"},
            {"id": 304, "name": "Mix Pulao"},
            {"id": 305, "name": "Mutter Pulao"},
            {"id": 306, "name": "Paneer Pulao"},
            {"id": 307, "name": "Veg. Biryani"},
        ],
    },

    {
        "id": "roti",
        "name": "Rotiyaan",
        "items": [
            {"id": 401, "name": "Roti"},
            {"id": 402, "name": "Butter Roti"},
            {"id": 403, "name": "Missi Roti"},
            {"id": 404, "name": "Dhania Roti"},
            {"id": 405, "name": "Laccha Parantha"},
            {"id": 406, "name": "Aloo Parantha"},
            {"id": 407, "name": "Gobhi Parantha"},
            {"id": 408, "name": "Missi Piyaz Parantha"},
            {"id": 409, "name": "Mirchi Lacha Parantha"},
            {"id": 410, "name": "Aloo Piyaz Parantha"},
            {"id": 411, "name": "Mooli Parantha"},
            {"id": 412, "name": "Mix Parantha"},
            {"id": 413, "name": "Paneer Stuff Parantha"},
            {"id": 414, "name": "Sada Naan"},
            {"id": 415, "name": "Butter Naan"},
            {"id": 416, "name": "Garlic Naan"},
            {"id": 417, "name": "Aloo Naan"},
            {"id": 418, "name": "Paneer Naan"},
            {"id": 419, "name": "Mix Naan"},
        ],
    },

    # -------- NEW CATEGORY: SNACKS --------
    {
        "id": "snacks",
        "name": "Snacks",
        "items": [
            {"id": 501, "name": "Cheese Chilly"},
            {"id": 502, "name": "Munchurian"},
            {"id": 503, "name": "Honey Chilli Potato"},
            {"id": 504, "name": "Paneer Pakora"},
            {"id": 505, "name": "Vegetable Pakora"},
            {"id": 506, "name": "Szechwan Chilli Potato"},
            {"id": 507, "name": "Chicken Pakora"},
            {"id": 508, "name": "Chicken Chilli"},
            {"id": 509, "name": "Burger"},
            {"id": 510, "name": "Noodles"},
            {"id": 511, "name": "Pao Bhaji"},
            {"id": 512, "name": "Idli Sambhar"},
            {"id": 513, "name": "Momos"},
            {"id": 514, "name": "Sandwich"},
            {"id": 515, "name": "Aalo Tikki"},
            {"id": 516, "name": "Chaat Papdi"},
            {"id": 517, "name": "Samosa"},
            {"id": 518, "name": "Kebab"},
            {"id": 519, "name": "Bhel Puri"},
        ],
    },
]

# -------- PERSISTENCE HELPERS --------
orders = []
next_order_id = 1


def load_state():
    """Load orders and next_order_id from DATA_FILE if it exists."""
    global orders, next_order_id
    if not os.path.exists(DATA_FILE):
        orders = []
        next_order_id = 1
        return

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        orders = data.get("orders", [])
        next_order_id = data.get("next_order_id", 1)

        # Ensure next_order_id is correct
        if orders:
            max_id = max(o.get("id", 0) for o in orders)
            if next_order_id <= max_id:
                next_order_id = max_id + 1

    except Exception as e:
        print("Failed to load state:", e)
        orders = []
        next_order_id = 1


def save_state():
    """Save orders and next_order_id to DATA_FILE."""
    data = {
        "orders": orders,
        "next_order_id": next_order_id,
    }
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print("Failed to save state:", e)


def all_menu_items_with_category():
    items = []
    for cat in MENU_CATEGORIES:
        for item in cat["items"]:
            items.append({
                "id": item["id"],
                "name": item["name"],
                "category_id": cat["id"],
                "category_name": cat["name"],
            })
    return items


# -------- ROUTES --------

@app.route("/")
def index():
    return redirect(url_for("order_page"))


@app.route("/order", methods=["GET"])
def order_page():
    return render_template("order.html", categories=MENU_CATEGORIES)


@app.route("/order", methods=["POST"])
def submit_order():
    global next_order_id, orders

    customer_name = request.form.get("customer_name", "").strip() or "Guest"
    table = request.form.get("table", "").strip()

    ordered_items = []

    for item in all_menu_items_with_category():
        qty_str = request.form.get(f"qty_{item['id']}")
        if not qty_str:
            continue

        try:
            qty = int(qty_str)
        except ValueError:
            qty = 0

        if qty > 0:
            ordered_items.append({
                "id": item["id"],
                "name": item["name"],
                "qty": qty,
                "category_id": item["category_id"],
                "category_name": item["category_name"],
            })

    if not ordered_items:
        return redirect(url_for("order_page"))

    order = {
        "id": next_order_id,
        "customer_name": customer_name,
        "table": table,
        "items": ordered_items,
        "status": "new",
        "created_at": datetime.now().strftime("%H:%M:%S"),
    }

    orders.append(order)
    next_order_id += 1
    save_state()

    return render_template("order.html", categories=MENU_CATEGORIES, success_order=order)


@app.route("/kitchen")
def kitchen_page():
    return render_template("kitchen.html")


@app.route("/api/orders")
def api_orders():
    pending = [o for o in orders if o.get("status") != "done"]
    return jsonify(pending)


@app.route("/api/orders/<int:order_id>/done", methods=["POST"])
def mark_order_done(order_id):
    for o in orders:
        if o.get("id") == order_id:
            o["status"] = "done"
            break

    save_state()
    return jsonify({"success": True})


# -------- INITIAL LOAD --------
load_state()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
