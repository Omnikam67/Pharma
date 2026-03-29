from fastapi import APIRouter
from langfuse import observe
from app.services.order_service import OrderService

router = APIRouter()
service = OrderService()

@router.post("/orders")
@observe(name="create_order_api")
def create_order(payload: dict):
    return service.create_order(**payload)
@router.get("/admin/orders")
def get_all_orders_with_user_info():
    return service.get_all_orders_with_user_info()


@router.get("/admin/order-analytics")
def get_order_analytics():
    """Get comprehensive order analytics for dashboard"""
    return service.get_order_analytics()


@router.post("/orders/{order_id}/cancel")
def cancel_order(order_id: int, payload: dict):
    patient_id = payload.get("patient_id") or payload.get("session_id")
    if not patient_id:
        return {"success": False, "message": "patient_id is required"}
    return service.cancel_order(order_id=order_id, patient_id=patient_id)


@router.put("/admin/orders/{order_id}/status")
def admin_set_order_status(order_id: int, payload: dict):
    status = payload.get("status")
    otp = payload.get("otp")
    return service.admin_set_order_status(order_id=order_id, status=status, otp=otp)
