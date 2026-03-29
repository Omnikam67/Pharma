import pandas as pd
from langfuse import observe
from app.core.database import SessionLocal
from app.core.models import Order, OrderItem, Product

HISTORY_FILE = r"C:\Users\hp\OneDrive\New folder\OneDrive\Desktop\Consumer Order History 1.xlsx"

class HistoryService:
    def __init__(self):
        try:
            self.df = pd.read_excel(HISTORY_FILE, header=4)
            self.df.columns = self.df.columns.str.strip()
            # Ensure Patient ID is a string for safe comparison
            if "Patient ID" in self.df.columns:
                self.df["Patient ID"] = self.df["Patient ID"].astype(str)
        except Exception as e:
            print(f"Failed to load Excel history file: {e}")
            self.df = pd.DataFrame()

    @observe(name="get_patient_history")
    def get_patient_history(self, patient_id: str):
        
        # 1. Get old history from the Excel file
        excel_history =[]
        if not self.df.empty and "Patient ID" in self.df.columns:
            excel_history = self.df[self.df["Patient ID"] == str(patient_id)].to_dict(orient="records")

        db_history = []
        db = SessionLocal()
        try:
            orders = db.query(Order).filter(Order.patient_id == str(patient_id)).all()
            for order in orders:
                for item in order.items:
                    product = db.query(Product).filter(Product.id == item.product_id).first()
                    date_str = order.order_date.strftime("%Y-%m-%d %H:%M:%S") if order.order_date else ""
                    db_history.append({
                        "order_id": order.id,
                        "Product Name": product.product_name if product else "Unknown",
                        "Quantity": item.quantity,
                        "Purchase date": date_str,
                        "Dosage frequency": "As directed",
                        "Status": order.status
                    })
        finally:
            db.close()

        return db_history[::-1] + excel_history

    @observe(name="get_all_history")
    def get_all_history(self):
        """Return normalized history rows across all patients for refill analysis."""
        rows = []

        # 1) Excel history (legacy sheet)
        if not self.df.empty:
            for _, rec in self.df.iterrows():
                patient_id = rec.get("Patient ID")
                product_name = rec.get("Product Name")
                quantity = rec.get("Quantity")
                purchase_date = rec.get("Purchase date")
                dosage_frequency = rec.get("Dosage frequency")

                if pd.isna(patient_id) or pd.isna(product_name):
                    continue

                # Normalize purchase date to YYYY-MM-DD where possible.
                date_norm = ""
                if not pd.isna(purchase_date):
                    try:
                        dt = pd.to_datetime(purchase_date, errors="coerce")
                        if pd.notna(dt):
                            date_norm = dt.strftime("%Y-%m-%d")
                        else:
                            date_norm = str(purchase_date).strip()
                    except Exception:
                        date_norm = str(purchase_date).strip()

                qty_norm = 0
                if not pd.isna(quantity):
                    try:
                        qty_norm = int(float(quantity))
                    except Exception:
                        qty_norm = 0

                rows.append({
                    "patient_id": str(patient_id),
                    "product_name": str(product_name),
                    "quantity": qty_norm,
                    "purchase_date": date_norm,
                    "dosage_frequency": "" if pd.isna(dosage_frequency) else str(dosage_frequency),
                })

        # 2) DB history (new orders)
        db = SessionLocal()
        try:
            orders = db.query(Order).all()
            for order in orders:
                date_norm = order.order_date.strftime("%Y-%m-%d") if order.order_date else ""
                for item in order.items:
                    product = db.query(Product).filter(Product.id == item.product_id).first()
                    rows.append({
                        "patient_id": str(order.patient_id),
                        "product_name": product.product_name if product else "Unknown",
                        "quantity": int(item.quantity or 0),
                        "purchase_date": date_norm,
                        "dosage_frequency": "daily",  # default for refill predictor
                    })
        finally:
            db.close()

        return rows
