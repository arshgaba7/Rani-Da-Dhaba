import os
from datetime import datetime
from zoneinfo import ZoneInfo  # Python 3.9+ timezone support

from flask import Flask, render_template, request, redirect, url_for, jsonify

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

app = Flask(__name__)

# ---------- TIMEZONE ----------
TORONTO_TZ = ZoneInfo("America/Toronto")

# ---------- DATABASE SETUP ----------

def get_database_url():
    """
    Use DATABASE_URL if provided (Render Postgres).
    Fallback to local SQLite for development.
    Also fix 'postgres://' -> 'postgresql://' for SQLAlchemy.
    """
    url = os.environ.get("DATABASE_URL")
    if url:
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url
    # Local dev fallback
    return "sqlite:///orders.db"


DATABASE_URL = get_database_url()
engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(100))
    table = Column(String(50))
    status = Column(String(20), default="new")
    # We'll set this explicitly in Python code using Toronto time
    created_at = Column(DateTime(timezone=True))

    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
        order_by="OrderItem.id",
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    item_id = Column(Integer)
    name = Column(String(100))
    category_id = Column(String(50))
    category_name = Column(String(100))
    qty = Column(Integer)

    order = relationship("Order", back_populates="items")


# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# ---------- MENU DEFINITION WITH CATEGORIES ----------

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
        "name": "Roti & Paratha",
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


def to_toronto_time(dt_obj: datetime) -> datetime:
    """Convert any datetime to Toronto local time for display."""
    if dt_obj is None:
        return None
    if dt_obj.tzinfo is None:
        # treat naive as UTC and convert to Toronto
        dt_obj = dt_obj.replace(tzinfo=ZoneInfo("UTC"))
    return dt_obj.astimezone(TORONTO_TZ)


# ---------- ROUTES ----------

@app.route("/")
def index():
    return redirect(url_for("order_page"))


@app.route("/order", methods=["GET"])
def order_page():
    return render_template("order.html", categories=MENU_CATEGORIES)


@app.route("/order", methods=["POST"])
def submit_order():
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
                "item_id": item["id"],
                "name": item["name"],
                "qty": qty,
                "category_id": item["category_id"],
                "category_name": item["category_name"],
            })

    if not ordered_items:
        return redirect(url_for("order_page"))

    session = SessionLocal()
    try:
        created_at = datetime.now(TORONTO_TZ)  # <-- Toronto time here

        order_db = Order(
            customer_name=customer_name,
            table=table,
            status="new",
            created_at=created_at,
        )
        session.add(order_db)
        session.flush()  # assigns order_db.id

        for it in ordered_items:
            oi = OrderItem(
                order_id=order_db.id,
                item_id=it["item_id"],
                name=it["name"],
                qty=it["qty"],
                category_id=it["category_id"],
                category_name=it["category_name"],
            )
            session.add(oi)

        session.commit()

        created_local = to_toronto_time(order_db.created_at)
        created_str = created_local.strftime("%H:%M:%S") if created_local else ""

        success_order = {
            "id": order_db.id,
            "customer_name": order_db.customer_name,
            "table": order_db.table,
            "status": order_db.status,
            "created_at": created_str,
            "items": ordered_items,
        }

    finally:
        session.close()

    return render_template(
        "order.html",
        categories=MENU_CATEGORIES,
        success_order=success_order,
    )


@app.route("/kitchen")
def kitchen_page():
    return render_template("kitchen.html")


@app.route("/api/orders")
def api_orders():
    session = SessionLocal()
    try:
        orders_db = (
            session.query(Order)
            .filter(Order.status != "done")
            .order_by(Order.id)
            .all()
        )

        result = []
        for o in orders_db:
            created_local = to_toronto_time(o.created_at)
            created_str = created_local.strftime("%H:%M:%S") if created_local else ""
            result.append({
                "id": o.id,
                "customer_name": o.customer_name,
                "table": o.table,
                "status": o.status,
                "created_at": created_str,
                "items": [
                    {
                        "id": it.item_id,
                        "name": it.name,
                        "qty": it.qty,
                        "category_id": it.category_id,
                        "category_name": it.category_name,
                    }
                    for it in o.items
                ],
            })
    finally:
        session.close()

    return jsonify(result)


@app.route("/api/orders/<int:order_id>/done", methods=["POST"])
def mark_order_done(order_id):
    session = SessionLocal()
    try:
        order = session.query(Order).filter_by(id=order_id).first()
        if order:
            order.status = "done"
            session.commit()
    finally:
        session.close()

    return jsonify({"success": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
