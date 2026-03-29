from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# ===== DOCTOR REGISTRATION & AUTH =====

class DoctorRegisterRequest(BaseModel):
    doctor_id: Optional[str] = None
    name: str
    email: str
    phone: str
    gender: Optional[str] = "Other"
    specialty: str  # e.g., "General Physician", "Cardiologist"
    experience_years: int
    qualification: str  # e.g., "MBBS", "MD"
    hospital_name: Optional[str] = None
    address: Optional[str] = None
    clinic_name: Optional[str] = None
    clinic_address: Optional[str] = None
    appointment_fee: Optional[float] = None  # Consultation fee
    password: str
    profile_image: Optional[str] = None
    degree_certificate_image: Optional[str] = None
    preferred_language: Optional[str] = "en"


class DoctorRegistrationApprovalRequest(BaseModel):
    doctor_id: str
    manager_id: str
    manager_password: Optional[str] = None
    approved: bool  # True to approve, False to deny
    reason: Optional[str] = None


class DoctorLoginRequest(BaseModel):
    doctor_id: Optional[str] = None
    email: Optional[str] = None
    password: str


class DoctorResponse(BaseModel):
    id: str
    doctor_id: str
    name: str
    email: str
    phone: str
    gender: str
    specialty: str
    experience_years: int
    qualification: str
    hospital_name: Optional[str] = None
    address: Optional[str] = None
    clinic_name: Optional[str] = None
    clinic_address: Optional[str] = None
    appointment_fee: Optional[float] = None  # Doctor's consultation fee
    profile_image: Optional[str] = None
    degree_certificate_image: Optional[str] = None
    availability: Optional[str] = None  # JSON string of availability schedule
    status: str  # "pending", "approved", "rejected"
    preferred_language: Optional[str] = "en"
    
    class Config:
        from_attributes = True


# ===== APPOINTMENT =====

class AppointmentRequest(BaseModel):
    doctor_id: str
    patient_name: str
    patient_phone: str
    patient_age: int
    patient_gender: str  # M, F, Other
    appointment_date: Optional[str] = None  # Format: YYYY-MM-DD
    appointment_time: Optional[str] = None  # Format: HH:MM
    notes: Optional[str] = None
    referral_id: Optional[str] = None
    

class AppointmentResponse(BaseModel):
    id: str
    doctor_id: str
    patient_name: str
    patient_phone: str
    patient_age: int
    patient_gender: str
    appointment_date: Optional[str]
    appointment_time: Optional[str]
    notes: Optional[str]
    status: str  # "pending", "approved", "completed", "cancelled"
    created_at: datetime
    
    class Config:
        from_attributes = True


class AppointmentActionRequest(BaseModel):
    appointment_id: str
    doctor_id: str
    action: str  # "approve" or "cancel"
    cancellation_reason: Optional[str] = None
    revenue_amount: Optional[float] = 0.0


class PrescriptionMedicineInput(BaseModel):
    medicine_name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    notes: Optional[str] = None


class AppointmentCompleteRequest(BaseModel):
    appointment_id: str
    doctor_id: str
    prescription_notes: Optional[str] = None
    medicines: List[PrescriptionMedicineInput] = Field(default_factory=list)


class ReferralCreateRequest(BaseModel):
    source_appointment_id: str
    from_doctor_id: str
    to_doctor_id: str
    reason: str
    clinical_notes: Optional[str] = None


class ReferredAppointmentBookingRequest(BaseModel):
    referral_id: str
    patient_name: str
    patient_phone: str
    patient_age: int
    patient_gender: str
    appointment_date: Optional[str] = None
    appointment_time: Optional[str] = None
    notes: Optional[str] = None


class DoctorFeedbackCreateRequest(BaseModel):
    appointment_id: str
    patient_phone: str
    rating: int = Field(ge=1, le=5)
    review_title: Optional[str] = None
    review_text: Optional[str] = None
    would_recommend: bool = True


# ===== REVENUE & ANALYTICS =====

class RevenueRecord(BaseModel):
    doctor_id: str
    appointment_id: str
    amount: float
    date: str
    
    class Config:
        from_attributes = True


class RevenueAnalyticsRequest(BaseModel):
    doctor_id: str
    filter_type: str  # "today", "week", "month", "custom"
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class RevenueAnalyticsResponse(BaseModel):
    total_revenue: float
    total_appointments: int
    approved_appointments: int
    cancelled_appointments: int
    daily_breakdown: dict  # {date: amount}
    top_hours: dict  # {hour: count}
    
    class Config:
        from_attributes = True


class DashboardStatsResponse(BaseModel):
    today_appointments: int
    today_revenue: float
    total_appointments: int
    total_revenue: float
    pending_requests: int
    approved_requests: int
    cancelled_requests: int
