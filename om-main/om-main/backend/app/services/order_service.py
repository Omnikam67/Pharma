import uuid
import secrets
from datetime import datetime, timedelta
from collections import defaultdict
from langfuse import observe
from app.core.database import SessionLocal
from app.core.models import Order, OrderItem, Product, User
from app.services.product_service import ProductService


class OrderService:
    @observe(name="create_order_service")
    def create_order(self, patient_id, product_id, quantity, total_price, product_name=None, delivery_location=None, delivery_map_url=None):
        db = SessionLocal()
        try:
            product = None
            if product_id:
                product = db.query(Product).filter(Product.product_id == str(product_id)).first()

            if not product and product_name:
                product = db.query(Product).filter(Product.product_name == product_name).first()

            if not product:
                product = Product(
                    product_id=str(product_id) if product_id else str(uuid.uuid4()),
                    product_name=product_name or "Unknown",
                    description=None,
                    stock=0,
                    price=float(total_price) / int(quantity) if quantity else 0,
                    prescription_required=False
                )
                db.add(product)
                db.flush()

            otp_code = f"{secrets.randbelow(1000000):06d}"
            order = Order(
                patient_id=patient_id,
                order_date=datetime.utcnow(),
                total_amount=float(total_price),
                status="pending",
                otp_code=otp_code,
                delivery_location=(delivery_location or "").strip() or None,
                delivery_map_url=(delivery_map_url or "").strip() or None,
            )
            db.add(order)
            db.flush()

            item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=int(quantity),
                price=float(total_price) / int(quantity) if quantity else 0
            )
            db.add(item)
            db.commit()

            return {
                "order_id": order.id,
                "patient_id": patient_id,
                "product_id": product.product_id,
                "product_name": product.product_name,
                "quantity": int(quantity),
                "total_price": float(total_price),
                "created_at": order.order_date,
                "status": order.status,
                "otp_code": order.otp_code,
                "delivery_location": order.delivery_location,
                "delivery_map_url": order.delivery_map_url,
            }
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    def get_all_orders_with_user_info(self):
        db = SessionLocal()
        try:
            orders = db.query(Order).all()
            results = []
            for order in orders:
                user = db.query(User).filter(User.id == order.patient_id).first()
                for item in order.items:
                    product = db.query(Product).filter(Product.id == item.product_id).first()
                    results.append({
                        "order_id": order.id,
                        "name": user.name if user else "Unknown",
                        "phone": user.phone if user else "N/A",
                        "product_name": product.product_name if product else "Unknown",
                        "delivery_location": order.delivery_location or "",
                        "delivery_map_url": order.delivery_map_url or "",
                        "price": item.price * item.quantity,
                        "quantity": item.quantity,
                        "date": order.order_date,
                        "status": order.status
                    })
            return results
        finally:
            db.close()

    def get_order_analytics(self):
        db = SessionLocal()
        try:
            orders = db.query(Order).filter(Order.status != "cancelled").all()
            total_orders = len(orders)
            total_revenue = sum(float(o.total_amount or 0) for o in orders)

            total_quantity_sold = 0
            product_sales = defaultdict(lambda: {"quantity": 0, "revenue": 0})

            for order in orders:
                for item in order.items:
                    product = db.query(Product).filter(Product.id == item.product_id).first()
                    name = product.product_name if product else "Unknown"
                    total_quantity_sold += int(item.quantity)
                    product_sales[name]["quantity"] += int(item.quantity)
                    product_sales[name]["revenue"] += float(item.price) * int(item.quantity)

            avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

            top_products = sorted(
                [{"name": k, "quantity": v["quantity"], "revenue": v["revenue"]} for k, v in product_sales.items()],
                key=lambda x: x["revenue"],
                reverse=True
            )[:5]

            orders_by_date = defaultdict(lambda: {"count": 0, "revenue": 0})
            today = datetime.utcnow().date()
            for order in orders:
                order_date = order.order_date.date() if order.order_date else today
                if (today - order_date).days <= 6:
                    key = order_date.isoformat()
                    orders_by_date[key]["count"] += 1
                    orders_by_date[key]["revenue"] += float(order.total_amount or 0)

            date_analytics = []
            for i in range(6, -1, -1):
                date = (today - timedelta(days=i)).isoformat()
                if date in orders_by_date:
                    date_analytics.append({
                        "date": date,
                        "orders": orders_by_date[date]["count"],
                        "revenue": round(orders_by_date[date]["revenue"], 2)
                    })
                else:
                    date_analytics.append({"date": date, "orders": 0, "revenue": 0})

            return {
                "total_orders": total_orders,
                "total_revenue": round(total_revenue, 2),
                "total_quantity_sold": total_quantity_sold,
                "avg_order_value": round(avg_order_value, 2),
                "top_products": top_products,
                "orders_by_date": date_analytics
            }
        finally:
            db.close()

    def cancel_order(self, order_id: int, patient_id: str):
        db = SessionLocal()
        product_service = ProductService()
        try:
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order:
                return {"success": False, "message": "Order not found"}
            if str(order.patient_id) != str(patient_id):
                return {"success": False, "message": "Unauthorized order cancel"}
            if order.status == "cancelled":
                return {"success": True, "message": "Order already cancelled", "status": order.status}

            restored = []
            for item in order.items:
                product = db.query(Product).filter(Product.id == item.product_id).first()
                if product:
                    # Restore stock in DB
                    product.stock = int(product.stock or 0) + int(item.quantity)
                    # Restore stock in Excel
                    restored_excel = product_service.add_stock(product.product_name, int(item.quantity))
                    restored.append({
                        "product_name": product.product_name,
                        "quantity": int(item.quantity),
                        "excel_updated": restored_excel
                    })

            order.status = "cancelled"
            order.updated_at = datetime.utcnow()
            db.commit()

            return {
                "success": True,
                "message": "Order cancelled",
                "order_id": order.id,
                "status": order.status,
                "restored_items": restored
            }
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    def admin_set_order_status(self, order_id: int, status: str, otp: str = None):
        db = SessionLocal()
        product_service = ProductService()
        try:
            status_norm = str(status or "").strip().lower()
            if status_norm not in {"completed", "cancelled"}:
                return {"success": False, "message": "Invalid status. Use 'completed' or 'cancelled'."}

            order = db.query(Order).filter(Order.id == order_id).first()
            if not order:
                return {"success": False, "message": "Order not found"}

            current = str(order.status or "").lower()
            if current == status_norm:
                return {
                    "success": True,
                    "message": f"Order already {status_norm}",
                    "order_id": order.id,
                    "status": order.status,
                }

            if status_norm == "completed":
                if current == "cancelled":
                    return {
                        "success": False,
                        "message": "Cancelled orders cannot be marked as completed.",
                        "order_id": order.id,
                        "status": order.status,
                    }

                submitted_otp = str(otp or "").strip()
                expected_otp = str(order.otp_code or "").strip()

                if not expected_otp:
                    return {
                        "success": False,
                        "message": "No OTP found for this order. Please create a new order with OTP support.",
                        "order_id": order.id,
                        "status": order.status,
                    }

                if not submitted_otp:
                    return {
                        "success": False,
                        "message": "OTP is required to mark this order as completed.",
                        "order_id": order.id,
                        "status": order.status,
                    }

                if submitted_otp != expected_otp:
                    return {
                        "success": False,
                        "message": "Invalid OTP. Order remains pending.",
                        "order_id": order.id,
                        "status": order.status,
                    }

                order.otp_verified_at = datetime.utcnow()

            # If changing to cancelled, restore stock exactly once.
            if status_norm == "cancelled" and current != "cancelled":
                for item in order.items:
                    product = db.query(Product).filter(Product.id == item.product_id).first()
                    if product:
                        product.stock = int(product.stock or 0) + int(item.quantity)
                        product_service.add_stock(product.product_name, int(item.quantity))

            order.status = status_norm
            order.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(order)

            return {
                "success": True,
                "message": f"Order marked as {status_norm}",
                "order_id": order.id,
                "status": order.status,
            }
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
