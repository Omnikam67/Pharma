import requests
from langfuse import observe
from app.services.product_service import ProductService
from app.services.vector_store import search_product


BACKEND_URL = "http://localhost:8000"


class SafetyAgent:
    def __init__(self):
        self.product_service = ProductService()
        
    @observe(name="validate_order_safety")
    def validate_order(self, patient_id, product_name, quantity, has_prescription, image_provided=False):

        if quantity <= 0:
            return {
                "approved": False,
                "reason": "Invalid quantity",
                "needs_prescription": False
            }
         # 2. Fetch Product Details (with typo-tolerant fallback)
        product = self.product_service.get_product_by_name(product_name)
        resolved_name = product_name
        if not product:
            try:
                candidate = search_product(product_name, n_results=1)
            except Exception:
                candidate = None
            if candidate:
                product = self.product_service.get_product_by_name(candidate)
                resolved_name = candidate

        if not product:
            alternatives = []
            try:
                alt_matches = search_product(product_name, n_results=3) or []
                alternatives = [m.get("name") for m in alt_matches if isinstance(m, dict) and m.get("name")]
            except Exception:
                alternatives = []
            alt_text = f" Did you mean: {', '.join(alternatives[:3])}?" if alternatives else ""
            return {
                "approved": False,
                "reason": f"Could not locate '{product_name}' in safety database.{alt_text}",
                "needs_prescription": False
            }

        # 3. PRESCRIPTION CHECK LOGIC
        requires_prescription = product.get("prescription_required", False)

        # ✅ FIX: Check `has_prescription` and return `needs_prescription: True`
        if requires_prescription and not has_prescription:
             return {
                       "approved": False,
                       "reason": f"Prescription required for {resolved_name}. Please upload an image.",
                       "needs_prescription": True
                }

        # If everything passes:
        return {
            "approved": True,
            "reason": "Safety checks passed",
            "needs_prescription": False
        }
