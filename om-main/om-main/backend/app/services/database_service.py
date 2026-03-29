"""
Database service examples - Shows how to use SQLAlchemy models
Replace your existing JSON operations with these database queries
"""

from sqlalchemy.orm import Session
from app.core.models import User, Product, Order, OrderItem, Reminder
from datetime import datetime, timedelta
import uuid
import hashlib

def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

# ==========================================
# USER OPERATIONS
# ==========================================

def create_user(db: Session, name: str, phone: str = None, shop_id: str = None, 
                password: str = None, age: int = None, role: str = "user"):
    """Create a new user (patient or admin)"""
    user = User(
        id=str(uuid.uuid4()),
        name=name,
        phone=phone,
        shop_id=shop_id,
        password_hash=hash_password(password),
        age=age,
        role=role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_id(db: Session, user_id: str):
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_phone(db: Session, phone: str):
    """Get user by phone number"""
    return db.query(User).filter(User.phone == phone).first()

def get_user_by_shop_id(db: Session, shop_id: str):
    """Get admin user by shop ID"""
    return db.query(User).filter(User.shop_id == shop_id).first()

def verify_password(db: Session, identifier: str, password: str):
    """Verify user credentials (phone or shop_id + password)"""
    user = db.query(User).filter(
        (User.phone == identifier) | (User.shop_id == identifier)
    ).first()
    
    if user and user.password_hash == hash_password(password):
        return user
    return None

def get_all_users(db: Session):
    """Get all users"""
    return db.query(User).all()

# ==========================================
# PRODUCT OPERATIONS
# ==========================================

def create_product(db: Session, product_name: str, price: float, stock: int = 0,
                   description: str = None, prescription_required: bool = False):
    """Create a new product"""
    product = Product(
        product_id=str(uuid.uuid4()),
        product_name=product_name,
        price=price,
        stock=stock,
        description=description,
        prescription_required=prescription_required
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

def get_product_by_id(db: Session, product_id: int):
    """Get product by ID"""
    return db.query(Product).filter(Product.id == product_id).first()

def get_product_by_name(db: Session, product_name: str):
    """Get product by name (case-insensitive)"""
    return db.query(Product).filter(
        Product.product_name.ilike(f"%{product_name}%")
    ).first()

def search_products(db: Session, search_term: str):
    """Search products by name or description"""
    return db.query(Product).filter(
        (Product.product_name.ilike(f"%{search_term}%")) |
        (Product.description.ilike(f"%{search_term}%"))
    ).all()

def get_all_products(db: Session):
    """Get all products"""
    return db.query(Product).all()

def get_low_stock_products(db: Session, threshold: int = 10):
    """Get products with low stock"""
    return db.query(Product).filter(Product.stock <= threshold).all()

def update_product_stock(db: Session, product_id: int, new_stock: int):
    """Update product stock level"""
    product = get_product_by_id(db, product_id)
    if product:
        product.stock = new_stock
        product.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(product)
    return product

# ==========================================
# ORDER OPERATIONS
# ==========================================

def create_order(db: Session, patient_id: str, items: list):
    """Create a new order with items
    items = [{"product_id": 1, "quantity": 2}, ...]
    """
    order = Order(patient_id=patient_id)
    total = 0.0
    
    for item in items:
        product = get_product_by_id(db, item["product_id"])
        if product:
            order_item = OrderItem(
                product_id=product.id,
                quantity=item["quantity"],
                price=product.price
            )
            order.items.append(order_item)
            total += product.price * item["quantity"]
            # Update stock
            product.stock -= item["quantity"]
    
    order.total_amount = total
    db.add(order)
    db.commit()
    db.refresh(order)
    return order

def get_order_by_id(db: Session, order_id: int):
    """Get order by ID"""
    return db.query(Order).filter(Order.id == order_id).first()

def get_user_orders(db: Session, patient_id: str):
    """Get all orders for a patient"""
    return db.query(Order).filter(Order.patient_id == patient_id).order_by(
        Order.order_date.desc()
    ).all()

def get_all_orders(db: Session):
    """Get all orders"""
    return db.query(Order).order_by(Order.order_date.desc()).all()

def update_order_status(db: Session, order_id: int, status: str):
    """Update order status"""
    order = get_order_by_id(db, order_id)
    if order:
        order.status = status
        order.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(order)
    return order

# ==========================================
# REMINDER OPERATIONS
# ==========================================

def create_reminder(db: Session, user_id: str, product_id: int, days: int = 0, hours: int = 1):
    """Create a medication refill reminder"""
    scheduled_date = datetime.utcnow() + timedelta(days=days, hours=hours)
    
    reminder = Reminder(
        user_id=user_id,
        product_id=product_id,
        scheduled_date=scheduled_date
    )
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder

def get_user_reminders(db: Session, user_id: str):
    """Get all reminders for a user"""
    return db.query(Reminder).filter(
        Reminder.user_id == user_id,
        Reminder.is_sent == False
    ).order_by(Reminder.scheduled_date).all()

def get_pending_reminders(db: Session):
    """Get all pending reminders that should be sent"""
    return db.query(Reminder).filter(
        Reminder.is_sent == False,
        Reminder.scheduled_date <= datetime.utcnow()
    ).all()

def mark_reminder_sent(db: Session, reminder_id: int):
    """Mark a reminder as sent"""
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if reminder:
        reminder.is_sent = True
        db.commit()
        db.refresh(reminder)
    return reminder

# ==========================================
# ANALYTICS & REPORTING
# ==========================================

def get_total_sales(db: Session):
    """Get total sales amount"""
    result = db.query(func.sum(Order.total_amount)).filter(
        Order.status == "completed"
    ).scalar()
    return result or 0.0

def get_sales_by_date_range(db: Session, start_date, end_date):
    """Get sales in a date range"""
    return db.query(Order).filter(
        Order.order_date >= start_date,
        Order.order_date <= end_date
    ).all()

def get_top_selling_products(db: Session, limit: int = 10):
    """Get most popular/sold products"""
    from sqlalchemy import func
    return db.query(
        Product.product_name,
        func.sum(OrderItem.quantity).label("total_sold")
    ).join(OrderItem).group_by(Product.id).order_by(
        func.sum(OrderItem.quantity).desc()
    ).limit(limit).all()

def get_inventory_stats(db: Session):
    """Get inventory statistics"""
    from sqlalchemy import func
    total_products = db.query(func.count(Product.id)).scalar()
    total_stock = db.query(func.sum(Product.stock)).scalar()
    low_stock = len(get_low_stock_products(db))
    
    return {
        "total_products": total_products,
        "total_stock": total_stock or 0,
        "low_stock_count": low_stock
    }

# ==========================================
# USAGE EXAMPLE
# ==========================================

"""
Example usage in your FastAPI routes:

from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.database_service import *

@app.post("/create-user")
def create_patient(name: str, phone: str, password: str, db: Session = Depends(get_db)):
    user = create_user(db, name=name, phone=phone, password=password, role="user")
    return {"id": user.id, "name": user.name, "phone": user.phone}

@app.get("/products")
def list_products(db: Session = Depends(get_db)):
    products = get_all_products(db)
    return products

@app.post("/orders")
def create_patient_order(patient_id: str, items: list, db: Session = Depends(get_db)):
    order = create_order(db, patient_id, items)
    return {"order_id": order.id, "total": order.total_amount}
"""
