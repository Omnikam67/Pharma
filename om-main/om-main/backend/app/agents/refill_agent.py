from datetime import datetime, timedelta
from langfuse import observe
from app.services.history_service import HistoryService


class RefillAgent:

    def __init__(self):
        self.history_service = HistoryService()

    @observe(name="check_refills")
    def check_refills(self, patient_id: str | None = None):

        history = self.history_service.get_all_history()
        alerts = []
        seen = set()

        for h in history:
            if patient_id and str(h.get("patient_id")) != str(patient_id):
                continue

            # Example fields from your Excel:
            # Patient id | Purchase date | Product Name | Quantity | Dosage frequency

            purchase_date = h.get("purchase_date")
            dosage = h.get("dosage_frequency", "").lower()
            quantity = h.get("quantity", 0)
            product_name = h.get("product_name")

            if not purchase_date or not dosage or not product_name:
                continue

            try:
                date_part = str(purchase_date).strip()[:10]
                last_purchase = datetime.strptime(date_part, "%Y-%m-%d")
            except Exception:
                continue

            # Only predict for daily medicines
            if "daily" in dosage:

                days_supply = int(quantity)

                next_needed = last_purchase + timedelta(days=days_supply)

                # If medicine will finish in next 3 days → alert
                if next_needed - datetime.now() <= timedelta(days=3):
                    key = (str(h.get("patient_id")), str(product_name), next_needed.strftime("%Y-%m-%d"))
                    if key in seen:
                        continue
                    seen.add(key)

                    alerts.append({
                        "patient_id": h.get("patient_id"),
                        "product_name": product_name,
                        "expected_refill_date": next_needed.strftime("%Y-%m-%d"),
                        "message": "Patient likely needs refill soon"
                    })

        alerts.sort(key=lambda x: x.get("expected_refill_date", "9999-99-99"))
        return alerts
