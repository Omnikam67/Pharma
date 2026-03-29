from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base

class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"

class User(Base):
    """User model for pharmacy (both patients and admins)"""
    __tablename__ = "users"

    id = Column(String(255), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    owner_name = Column(String(255), nullable=True)
    store_name = Column(String(255), nullable=True)
    phone = Column(String(20), unique=True, nullable=True, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    shop_id = Column(String(255), unique=True, nullable=True, index=True)
    pharma_id = Column(String(255), unique=True, nullable=True, index=True)
    address = Column(Text, nullable=True)
    store_address = Column(Text, nullable=True)
    pharmacy_address = Column(Text, nullable=True)
    pharmacy_license_number = Column(String(255), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=False)
    password_reset_otp = Column(String(6), nullable=True)
    password_reset_expires_at = Column(DateTime, nullable=True)
    age = Column(Integer, nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    preferred_language = Column(String(10), default="en", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    orders = relationship("Order", back_populates="patient", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="user", cascade="all, delete-orphan")
    trusted_contacts = relationship("UserTrustedContact", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.name} ({self.role})>"


class Product(Base):
    """Medicine/Product model"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String(255), unique=True, index=True)
    product_name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    stock = Column(Integer, default=0)
    price = Column(Float, nullable=False)
    prescription_required = Column(Boolean, default=False)
    manufacturer = Column(String(255), nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    orders = relationship("OrderItem", back_populates="product", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="product", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Product {self.product_name} (₹{self.price})>"


class Order(Base):
    """Order/Purchase model"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(255), ForeignKey("users.id"), nullable=False, index=True)
    order_date = Column(DateTime, default=datetime.utcnow, index=True)
    total_amount = Column(Float, default=0.0)
    status = Column(String(50), default="pending")  # pending, completed, cancelled
    otp_code = Column(String(6), nullable=True, index=True)
    otp_verified_at = Column(DateTime, nullable=True)
    delivery_location = Column(Text, nullable=True)
    delivery_map_url = Column(Text, nullable=True)
    delivery_boy_id = Column(String(255), ForeignKey("delivery_boys.id"), nullable=True, index=True)
    delivery_cancel_reason = Column(Text, nullable=True)
    delivery_completed_at = Column(DateTime, nullable=True)
    delivery_cancelled_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    delivery_boy = relationship("DeliveryBoy", back_populates="orders")

    def __repr__(self):
        return f"<Order {self.id} - Patient {self.patient_id}>"


class OrderItem(Base):
    """Individual items in an order"""
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)  # Price at time of purchase

    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="orders")

    def __repr__(self):
        return f"<OrderItem {self.quantity}x {self.product_id}>"


class Reminder(Base):
    """Medication refill reminders"""
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), ForeignKey("users.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    scheduled_date = Column(DateTime, nullable=False, index=True)
    is_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="reminders")
    product = relationship("Product", back_populates="reminders")

    def __repr__(self):
        return f"<Reminder {self.user_id} - {self.product_id}>"


class ChatHistory(Base):
    """Store chat conversations for analytics"""
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True)
    user_id = Column(String(255), ForeignKey("users.id"), nullable=True, index=True)
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<ChatHistory {self.session_id}>"


class UserTrustedContact(Base):
    """Manually imported trusted phone contacts for review matching."""
    __tablename__ = "user_trusted_contacts"

    id = Column(String(255), primary_key=True, index=True)
    user_id = Column(String(255), ForeignKey("users.id"), nullable=False, index=True)
    contact_phone = Column(String(20), nullable=False, index=True)
    source = Column(String(50), nullable=False, default="manual_upload")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="trusted_contacts")

    def __repr__(self):
        return f"<UserTrustedContact {self.user_id} -> {self.contact_phone}>"


class DeliveryBoy(Base):
    """Delivery personnel pending/approved by system manager"""
    __tablename__ = "delivery_boys"

    id = Column(String(255), primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=False, default="Other")
    password_hash = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default="pending", index=True)
    rejection_reason = Column(Text, nullable=True)
    approved_by = Column(String(255), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    orders = relationship("Order", back_populates="delivery_boy")

    def __repr__(self):
        return f"<DeliveryBoy {self.name} ({self.status})>"
