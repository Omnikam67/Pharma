from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from langfuse import observe
import time
import threading
import os

from app.agents.refill_agent import RefillAgent
from app.agents.execution_agent import send_notification
from app.services.user_service import UserService

router = APIRouter(prefix="/refill", tags=["Refill Intelligence"])

class ReminderRequest(BaseModel):
    patient_id: str
    product_name: str
    days: int = 0
    hours: int = 0


class RefillWhatsappRequest(BaseModel):
    patient_id: str

def wait_and_send_whatsapp(phone: str, product_name: str, delay_seconds: int):
    """Wait and then send a WhatsApp message via Twilio (synchronous version)."""
    time.sleep(delay_seconds)
    
    msg = (
        f"⏰ *Refill Reminder from Agentic Pharmacy!*\n\n"
        f"It's time to check your stock or take your medicine: *{product_name}*.\n\n"
        f"Reply to this chat if you would like me to order a refill for you! 🏥"
    )
    # Re-using the Twilio function from execution_agent
    try:
        send_notification(phone, msg)
    except Exception as e:
        print(f"Error sending WhatsApp reminder: {e}")

@router.get("/refill-alerts")
@observe(name="get_refill_alerts")
def get_alerts():
    agent = RefillAgent()
    return agent.check_refills()


@router.post("/send-alerts-whatsapp")
@observe(name="send_refill_alerts_whatsapp")
def send_refill_alerts_whatsapp(req: RefillWhatsappRequest):
    user = UserService.get_user(req.patient_id)
    if not user or not user.get("phone"):
        return {"success": False, "message": "Could not find your phone number."}

    sid = os.getenv("TWILIO_ACCOUNT_SID")
    token = os.getenv("TWILIO_AUTH_TOKEN")
    from_num = os.getenv("TWILIO_WHATSAPP_FROM")
    if not sid or not token or not from_num:
        return {"success": False, "message": "WhatsApp service is not configured on server."}

    agent = RefillAgent()
    alerts = agent.check_refills(patient_id=req.patient_id)
    if not alerts:
        return {"success": True, "sent": 0, "message": "No refill alerts pending right now."}

    phone = user.get("phone")
    formatted_phone = phone if phone.startswith("+") else f"+91{phone}"

    lines = [
        f"- {a.get('product_name')}: needed by {a.get('expected_refill_date')}"
        for a in alerts[:20]
    ]
    body = "🔔 *Medication Refill Alerts*\n\n" + "\n".join(lines)
    try:
        send_notification(formatted_phone, body)
        return {"success": True, "sent": min(len(alerts), 20), "message": "Refill alerts sent to your WhatsApp."}
    except Exception as e:
        return {"success": False, "message": f"Failed to send WhatsApp alerts: {e}"}

@router.post("/schedule-reminder")
def schedule_reminder(req: ReminderRequest, background_tasks: BackgroundTasks):
    # 1. Fetch User to get phone number
    user = UserService.get_user(req.patient_id)
    if not user or not user.get("phone"):
        return {"success": False, "message": "Could not find your phone number to send WhatsApp."}
    
    phone = user.get("phone")
    formatted_phone = phone if phone.startswith("+") else f"+91{phone}"
    
    # 2. Calculate delay in seconds
    total_seconds = (req.days * 24 * 3600) + (req.hours * 3600)
    
    if total_seconds <= 0:
        return {"success": False, "message": "Time must be greater than 0."}

    # 3. Schedule the background task (does not block the server)
    # Using threading for better compatibility with sync functions
    background_tasks.add_task(wait_and_send_whatsapp, formatted_phone, req.product_name, total_seconds)
    
    return {
        "success": True, 
        "message": f"✅ Reminder successfully set! You will receive a WhatsApp message in {req.days} day(s) and {req.hours} hour(s)."
    }
