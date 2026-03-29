"""
WhatsApp notification helpers for doctor appointment flows.
"""

import os
from typing import Optional

import httpx
from dotenv import load_dotenv

load_dotenv()


class WhatsAppService:
    """Service for sending WhatsApp messages via Twilio."""

    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM", "+14155552671")

    @staticmethod
    def format_whatsapp_sender(sender: str) -> str:
        clean_sender = (sender or "").strip()
        if clean_sender.startswith("whatsapp:"):
            return clean_sender
        return f"whatsapp:{clean_sender}"

    @staticmethod
    def format_phone_number(phone: str) -> str:
        digits = "".join(filter(str.isdigit, phone or ""))
        if not phone.startswith("+"):
            if len(digits) == 10:
                return f"+91{digits}"
            if len(digits) == 12 and digits.startswith("91"):
                return f"+{digits}"
        return phone if (phone or "").startswith("+") else f"+{digits}"

    @staticmethod
    def send_appointment_approved(
        patient_phone: str,
        doctor_name: str,
        appointment_date: Optional[str] = None,
        appointment_time: Optional[str] = None,
    ) -> dict:
        formatted_phone = WhatsAppService.format_phone_number(patient_phone)
        lines = [
            "Appointment Confirmed",
            "",
            f"Your appointment with Dr. {doctor_name} has been approved.",
        ]
        if appointment_date:
            lines.append(f"Date: {appointment_date}")
        if appointment_time:
            lines.append(f"Time: {appointment_time}")
        lines.extend(["", "Please reach on time. If you need to reschedule, contact us.", "", "Thank you."])
        return WhatsAppService._send_message(formatted_phone, "\n".join(lines))

    @staticmethod
    def send_appointment_cancelled(
        patient_phone: str,
        doctor_name: str,
        reason: Optional[str] = None,
    ) -> dict:
        formatted_phone = WhatsAppService.format_phone_number(patient_phone)
        lines = [
            "Appointment Cancelled",
            "",
            f"Your appointment with Dr. {doctor_name} has been cancelled.",
        ]
        if reason:
            lines.extend(["", f"Reason: {reason}"])
        lines.extend(["", "Please contact us to reschedule or book another appointment."])
        return WhatsAppService._send_message(formatted_phone, "\n".join(lines))

    @staticmethod
    def send_appointment_reminder(
        patient_phone: str,
        doctor_name: str,
        appointment_time: str,
    ) -> dict:
        formatted_phone = WhatsAppService.format_phone_number(patient_phone)
        message = (
            "Appointment Reminder\n\n"
            f"Your appointment with Dr. {doctor_name} is at {appointment_time} today.\n\n"
            "Please arrive 10 minutes early."
        )
        return WhatsAppService._send_message(formatted_phone, message)

    @staticmethod
    def send_doctor_approval_notification(
        doctor_phone: str,
        doctor_name: str,
    ) -> dict:
        formatted_phone = WhatsAppService.format_phone_number(doctor_phone)
        message = (
            "Account Approved\n\n"
            f"Welcome Dr. {doctor_name}.\n\n"
            "Your account has been approved and you can now log in to the platform."
        )
        return WhatsAppService._send_message(formatted_phone, message)

    @staticmethod
    def send_appointment_completed(
        patient_phone: str,
        doctor_name: str,
        prescription_image: Optional[str] = None,
        medicines: Optional[list] = None,
        prescription_notes: Optional[str] = None,
    ) -> dict:
        formatted_phone = WhatsAppService.format_phone_number(patient_phone)
        lines = [
            "Appointment Completed",
            "",
            f"Your consultation with Dr. {doctor_name} has been completed.",
            "",
            "Prescription summary:",
        ]
        for idx, medicine in enumerate(medicines or [], start=1):
            parts = [medicine.get("medicine_name", "Medicine")]
            if medicine.get("dosage"):
                parts.append(medicine["dosage"])
            if medicine.get("frequency"):
                parts.append(medicine["frequency"])
            if medicine.get("duration"):
                parts.append(medicine["duration"])
            lines.append(f"{idx}. " + " | ".join(parts))
        if prescription_notes:
            lines.extend(["", f"Notes: {prescription_notes}"])

        media_urls = [prescription_image] if prescription_image and prescription_image.startswith("http") else None
        result = WhatsAppService._send_message(formatted_phone, "\n".join(lines), media_urls=media_urls)
        if prescription_image and not media_urls:
            result["note"] = (
                "Prescription image was generated, but WhatsApp media delivery needs a public URL. "
                "The prescription summary was sent as text."
            )
        return result

    @staticmethod
    def _send_message(to_phone: str, message: str, media_urls: Optional[list[str]] = None) -> dict:
        if not WhatsAppService.TWILIO_ACCOUNT_SID or not WhatsAppService.TWILIO_AUTH_TOKEN:
            print(f"[WhatsApp Log] To: {to_phone}")
            print(f"[WhatsApp Log] Message: {message}")
            if media_urls:
                print(f"[WhatsApp Log] Media: {media_urls}")
            return {
                "success": True,
                "message": "Message logged (WhatsApp service disabled)",
                "note": "Configure Twilio for actual WhatsApp delivery",
            }

        try:
            url = f"https://api.twilio.com/2010-04-01/Accounts/{WhatsAppService.TWILIO_ACCOUNT_SID}/Messages.json"
            auth = (WhatsAppService.TWILIO_ACCOUNT_SID, WhatsAppService.TWILIO_AUTH_TOKEN)
            data = {
                "From": WhatsAppService.format_whatsapp_sender(WhatsAppService.TWILIO_WHATSAPP_FROM),
                "To": f"whatsapp:{to_phone}",
                "Body": message,
            }
            for idx, media_url in enumerate(media_urls or []):
                data[f"MediaUrl{idx}"] = media_url

            response = httpx.post(url, data=data, auth=auth, timeout=8.0)
            if response.status_code in [200, 201]:
                return {
                    "success": True,
                    "message": "WhatsApp message sent successfully",
                    "sid": response.json().get("sid"),
                }
            if response.status_code == 400 and "21212" in response.text:
                print(f"[WhatsApp Fallback] To: {to_phone}")
                print(f"[WhatsApp Fallback] Message: {message}")
                return {
                    "success": True,
                    "message": "WhatsApp sender is invalid in Twilio config. Message logged for local testing.",
                    "note": response.text,
                }
            return {"success": False, "message": f"Failed to send WhatsApp: {response.text}"}
        except Exception as exc:
            print(f"WhatsApp send error: {exc}")
            return {"success": False, "message": str(exc)}

    @staticmethod
    def send_bulk_appointment_reminders(appointments: list) -> dict:
        results = {"total": len(appointments), "success": 0, "failed": 0, "errors": []}
        for appointment in appointments:
            result = WhatsAppService.send_appointment_reminder(
                appointment.get("patient_phone"),
                appointment.get("doctor_name"),
                appointment.get("appointment_time"),
            )
            if result.get("success"):
                results["success"] += 1
            else:
                results["failed"] += 1
                results["errors"].append(
                    {"phone": appointment.get("patient_phone"), "error": result.get("message")}
                )
        return results


async def send_whatsapp_async(message_type: str, patient_phone: str, doctor_name: str, **kwargs) -> dict:
    """Async wrapper for WhatsApp service."""

    if message_type == "appointment_approved":
        return WhatsAppService.send_appointment_approved(
            patient_phone,
            doctor_name,
            kwargs.get("appointment_date"),
            kwargs.get("appointment_time"),
        )
    if message_type == "appointment_cancelled":
        return WhatsAppService.send_appointment_cancelled(
            patient_phone,
            doctor_name,
            kwargs.get("reason"),
        )
    if message_type == "appointment_reminder":
        return WhatsAppService.send_appointment_reminder(
            patient_phone,
            doctor_name,
            kwargs.get("appointment_time"),
        )
    if message_type == "doctor_approval":
        return WhatsAppService.send_doctor_approval_notification(patient_phone, doctor_name)
    if message_type == "appointment_completed":
        return WhatsAppService.send_appointment_completed(
            patient_phone,
            doctor_name,
            kwargs.get("prescription_image"),
            kwargs.get("medicines"),
            kwargs.get("prescription_notes"),
        )
    return {"success": False, "message": f"Unknown message type: {message_type}"}
