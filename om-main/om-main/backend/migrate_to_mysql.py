"""
One-time migration to MySQL.
Imports users from users_database.json, products from Excel, and orders from order_history.json.
"""

import json
import uuid
import hashlib
from datetime import datetime
from pathlib import Path

import pandas as pd

from app.core.database import SessionLocal, Base, engine, init_db
from app.core.models import User, UserRole, Product, Order, OrderItem


BASE_DIR = Path(__file__).parent
USERS_JSON = BASE_DIR / "users_database.json"
ORDERS_JSON = BASE_DIR / "order_history.json"
PRODUCT_XLSX = Path(r"C:\Users\hp\Downloads\Final product.xlsx")


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def safe_float(value, default=0.0):
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def safe_int(value, default=0):
    try:
        if value is None:
            return default
        return int(value)
    except Exception:
        return default


def safe_bool(value, default=False):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "y"}
    return default


def parse_dt(value):
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except Exception:
            pass
    return datetime.utcnow()


def create_tables():
    Base.metadata.create_all(bind=engine)


def migrate_users(db):
    if not USERS_JSON.exists():
        print("users_database.json not found, skipping users.")
        return 0
    with open(USERS_JSON, "r") as f:
        data = json.load(f)
    users = data.values() if isinstance(data, dict) else data
    count = 0
    for u in users:
        user_id = u.get("id") or str(uuid.uuid4())
        existing = db.query(User).filter(User.id == user_id).first()
        if existing:
            continue
        role = u.get("role", "user")
        preferred_language = u.get("preferred_language") or "en"
        db_user = User(
            id=user_id,
            name=u.get("name", "Unknown"),
            phone=u.get("phone"),
            shop_id=u.get("shop_id"),
            password_hash=hash_password(u.get("password", "password")),
            age=u.get("age"),
            role=UserRole(role),
            preferred_language=preferred_language
        )
        db.add(db_user)
        count += 1
    return count


def migrate_products(db):
    if not PRODUCT_XLSX.exists():
        print("Product Excel not found, skipping products.")
        return 0
    df = pd.read_excel(PRODUCT_XLSX, header=0)
    df.columns = [str(c).strip().lower() for c in df.columns]
    count = 0
    for _, row in df.iterrows():
        product_id = str(row.get("product id") or "").strip()
        product_name = str(row.get("product name") or "").strip()
        if not product_name:
            continue
        price = safe_float(row.get("price rec", row.get("price", 0)))
        stock = safe_int(row.get("stock", 0))
        description = row.get("descriptions", row.get("short descriptions", row.get("product descriptions", None)))
        presc_val = row.get("prescription_required", row.get("prescription record", row.get("prescription", False)))
        prescription_required = safe_bool(presc_val, False)

        existing = None
        if product_id:
            existing = db.query(Product).filter(Product.product_id == product_id).first()
        if not existing:
            existing = db.query(Product).filter(Product.product_name == product_name).first()
        if existing:
            continue
        db_product = Product(
            product_id=product_id or str(uuid.uuid4()),
            product_name=product_name,
            description=str(description) if description is not None else None,
            stock=stock,
            price=price,
            prescription_required=prescription_required
        )
        db.add(db_product)
        count += 1
    return count


def migrate_orders(db):
    if not ORDERS_JSON.exists():
        print("order_history.json not found, skipping orders.")
        return 0
    with open(ORDERS_JSON, "r") as f:
        orders = json.load(f)
    count = 0
    for o in orders:
        patient_id = str(o.get("patient_id"))
        quantity = safe_int(o.get("quantity", 0))
        total_price = safe_float(o.get("total_price", 0))
        created_at = parse_dt(o.get("created_at"))
        product_name = o.get("product_name") or "Unknown"

        product = db.query(Product).filter(Product.product_name == product_name).first()
        if not product:
            product = Product(
                product_id=str(uuid.uuid4()),
                product_name=product_name,
                description=None,
                stock=0,
                price=total_price / quantity if quantity else 0,
                prescription_required=False
            )
            db.add(product)
            db.flush()

        existing_order = db.query(Order).filter(
            Order.patient_id == patient_id,
            Order.order_date == created_at,
            Order.total_amount == total_price
        ).first()
        if existing_order:
            continue

        order = Order(
            patient_id=patient_id,
            order_date=created_at,
            total_amount=total_price,
            status="created"
        )
        db.add(order)
        db.flush()

        item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=quantity,
            price=total_price / quantity if quantity else 0
        )
        db.add(item)
        count += 1
    return count


def main():
    init_db()
    db = SessionLocal()
    try:
        u = migrate_users(db)
        p = migrate_products(db)
        o = migrate_orders(db)
        db.commit()
        print(f"Imported users: {u}")
        print(f"Imported products: {p}")
        print(f"Imported orders: {o}")
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    main()
