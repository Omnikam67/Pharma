"""
Database initialization script
Run this once to create all tables and seed initial data
"""

import json
from app.core.database import init_db, SessionLocal, engine, Base
from app.core.models import User, Product, Order, OrderItem, Reminder, ChatHistory, UserRole
import uuid
from datetime import datetime
import hashlib

def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

def seed_initial_data():
    """Seed initial test data from JSON files"""
    db = SessionLocal()
    
    try:
        print("\nSeeding initial data...")
        
        # Load users from JSON
        try:
            with open('users_database.json', 'r') as f:
                users_data = json.load(f)
                for user_data in users_data:
                    user = User(
                        id=user_data.get('id', str(uuid.uuid4())),
                        name=user_data.get('name', 'Unknown'),
                        phone=user_data.get('phone'),
                        shop_id=user_data.get('shop_id'),
                        password_hash=hash_password(user_data.get('password', 'password')),
                        age=user_data.get('age'),
                        role=UserRole(user_data.get('role', 'user'))
                    )
                    db.add(user)
                print(f"Added {len(users_data)} users")
        except FileNotFoundError:
            print("users_database.json not found")
        
        # Load products from mock warehouse
        try:
            mock_data = {
                "Paracetamol": {"price": 50, "stock": 100, "prescription_required": False},
                "Ibuprofen": {"price": 80, "stock": 80, "prescription_required": False},
                "Amoxicillin": {"price": 120, "stock": 50, "prescription_required": True},
                "Metformin": {"price": 100, "stock": 60, "prescription_required": True},
                "Vitamin C": {"price": 40, "stock": 200, "prescription_required": False},
            }
            
            for name, details in mock_data.items():
                product = Product(
                    product_id=str(uuid.uuid4()),
                    product_name=name,
                    description=f"Pharmaceutical product: {name}",
                    stock=details["stock"],
                    price=details["price"],
                    prescription_required=details["prescription_required"]
                )
                db.add(product)
            print(f"Added {len(mock_data)} products")
        except Exception as e:
            print(f"Error loading products: {e}")
        
        db.commit()
        print("\nDatabase seeding completed.")
        
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

def reset_database():
    """Drop all tables and recreate (useful for development)"""
    print("\nDropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Tables dropped.")
    create_tables()
    seed_initial_data()

if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("PHARMACY DATABASE INITIALIZATION")
    print("=" * 60)
    
    if len(sys.argv) > 1 and sys.argv[1] == "reset":
        reset_database()
    else:
        create_tables()
        seed_initial_data()
    
    print("\n" + "=" * 60)
    print("Database is ready.")
    print("=" * 60)
