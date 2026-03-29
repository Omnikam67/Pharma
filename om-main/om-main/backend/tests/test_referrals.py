from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.core.doctor_models import AppointmentRequestTable, DoctorRegistrationRequest, DoctorTable
from app.services import doctor_service as doctor_service_module
from app.services.doctor_service import DoctorService
from app.services.whatsapp_service import WhatsAppService


def test_referral_flow(monkeypatch):
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    monkeypatch.setattr(doctor_service_module, "SessionLocal", TestingSessionLocal)
    monkeypatch.setattr(WhatsAppService, "send_appointment_approved", staticmethod(lambda **kwargs: {"success": True}))
    monkeypatch.setattr(WhatsAppService, "send_appointment_cancelled", staticmethod(lambda **kwargs: {"success": True}))
    monkeypatch.setattr(WhatsAppService, "send_appointment_completed", staticmethod(lambda **kwargs: {"success": True}))

    db = TestingSessionLocal()
    doctor_a = DoctorTable(
        doctor_id="doc-a",
        name="Doctor A",
        email="a@example.com",
        phone="1111111111",
        password_hash="hash",
        specialty="General Physician",
        gender="Other",
        experience_years=5,
        qualification="MBBS",
        clinic_name="Clinic A",
        status="approved",
    )
    doctor_b = DoctorTable(
        doctor_id="doc-b",
        name="Doctor B",
        email="b@example.com",
        phone="2222222222",
        password_hash="hash",
        specialty="Cardiologist",
        gender="Other",
        experience_years=8,
        qualification="MD",
        clinic_name="Clinic B",
        status="approved",
    )
    db.add_all([doctor_a, doctor_b])
    db.commit()
    db.close()

    appointment_result = DoctorService.create_appointment_request(
        doctor_id="doc-a",
        patient_name="Patient One",
        patient_phone="9999999999",
        patient_age=47,
        patient_gender="M",
        appointment_date="2026-03-24",
        appointment_time="10:30",
        notes="Initial consultation",
    )
    assert appointment_result["success"] is True
    source_appointment_id = appointment_result["appointment_id"]

    approved_result = DoctorService.approve_appointment(source_appointment_id, revenue_amount=500)
    assert approved_result["success"] is True

    referral_result = DoctorService.create_referral(
        source_appointment_id=source_appointment_id,
        from_doctor_id="doc-a",
        to_doctor_id="doc-b",
        reason="Cardiac symptoms need specialist review",
        clinical_notes="Patient reports chest discomfort and fatigue.",
    )
    assert referral_result["success"] is True
    referral_id = referral_result["referral"]["id"]
    assert referral_result["referral"]["status"] == "pending_booking"

    patient_referrals = DoctorService.get_referrals_for_patient("9999999999")
    assert len(patient_referrals) == 1
    assert patient_referrals[0]["to_doctor_name"] == "Doctor B"

    referred_appointment_result = DoctorService.create_appointment_request(
        doctor_id="doc-b",
        patient_name="Patient One",
        patient_phone="9999999999",
        patient_age=47,
        patient_gender="M",
        appointment_date="2026-03-25",
        appointment_time="11:00",
        notes="Follow-up with specialist",
        referral_id=referral_id,
    )
    assert referred_appointment_result["success"] is True

    referral_detail = DoctorService.get_referral_detail(referral_id)
    assert referral_detail["status"] == "booked"
    referred_appointment_id = referral_detail["referred_appointment_id"]
    assert referred_appointment_id

    approved_specialist = DoctorService.approve_appointment(referred_appointment_id, revenue_amount=800)
    assert approved_specialist["success"] is True
    referral_detail = DoctorService.get_referral_detail(referral_id)
    assert referral_detail["status"] == "approved"

    completed_specialist = DoctorService.complete_appointment(
        appointment_id=referred_appointment_id,
        doctor_id="doc-b",
        prescription_notes="Follow up after 7 days.",
        medicines=[
            {
                "medicine_name": "Aspirin",
                "frequency": "Once daily",
                "duration": "7 days",
                "notes": "After breakfast",
            }
        ],
    )
    assert completed_specialist["success"] is True

    final_referral = DoctorService.get_referral_detail(referral_id)
    assert final_referral["status"] == "completed"
    assert final_referral["result_appointment"]["status"] == "completed"
    assert final_referral["result_appointment"]["prescription_medicines"][0]["medicine_name"] == "Aspirin"

    source_referrals = DoctorService.get_referrals_for_source_doctor("doc-a")
    assert len(source_referrals) == 1
    assert source_referrals[0]["result_appointment"]["has_prescription_image"] is True


def test_feedback_targets_final_referral_doctor(monkeypatch):
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    monkeypatch.setattr(doctor_service_module, "SessionLocal", TestingSessionLocal)
    monkeypatch.setattr(WhatsAppService, "send_appointment_approved", staticmethod(lambda **kwargs: {"success": True}))
    monkeypatch.setattr(WhatsAppService, "send_appointment_cancelled", staticmethod(lambda **kwargs: {"success": True}))
    monkeypatch.setattr(WhatsAppService, "send_appointment_completed", staticmethod(lambda **kwargs: {"success": True}))

    db = TestingSessionLocal()
    doctor_a = DoctorTable(
        doctor_id="doc-a",
        name="Doctor A",
        email="a@example.com",
        phone="1111111111",
        password_hash="hash",
        specialty="General Physician",
        gender="Other",
        experience_years=5,
        qualification="MBBS",
        clinic_name="Clinic A",
        status="approved",
    )
    doctor_b = DoctorTable(
        doctor_id="doc-b",
        name="Doctor B",
        email="b@example.com",
        phone="2222222222",
        password_hash="hash",
        specialty="Cardiologist",
        gender="Other",
        experience_years=8,
        qualification="MD",
        clinic_name="Clinic B",
        status="approved",
    )
    db.add_all([doctor_a, doctor_b])
    db.commit()
    db.close()

    source = DoctorService.create_appointment_request(
        doctor_id="doc-a",
        patient_name="Patient One",
        patient_phone="9999999999",
        patient_age=47,
        patient_gender="M",
    )
    source_id = source["appointment_id"]
    DoctorService.approve_appointment(source_id, revenue_amount=500)

    referral = DoctorService.create_referral(
        source_appointment_id=source_id,
        from_doctor_id="doc-a",
        to_doctor_id="doc-b",
        reason="Refer to cardiologist",
        clinical_notes="Needs specialist review",
    )["referral"]

    referred = DoctorService.create_appointment_request(
        doctor_id="doc-b",
        patient_name="Patient One",
        patient_phone="9999999999",
        patient_age=47,
        patient_gender="M",
        referral_id=referral["id"],
    )
    referred_id = referred["appointment_id"]
    DoctorService.approve_appointment(referred_id, revenue_amount=800)
    DoctorService.complete_appointment(
        appointment_id=referred_id,
        doctor_id="doc-b",
        prescription_notes="Continue treatment",
        medicines=[{"medicine_name": "Aspirin"}],
    )

    history = DoctorService.get_patient_appointment_history("9999999999")
    source_card = next(item for item in history if item["id"] == source_id)
    referred_card = next(item for item in history if item["id"] == referred_id)

    assert source_card["feedback"]["show_on_card"] is False
    assert source_card["feedback"]["target_doctor_name"] == "Doctor B"
    assert referred_card["feedback"]["show_on_card"] is True
    assert referred_card["feedback"]["can_submit"] is True

    feedback = DoctorService.submit_doctor_feedback(
        appointment_id=referred_id,
        patient_phone="9999999999",
        rating=5,
        review_title="Very good heart specialist",
        review_text="Explained the treatment clearly.",
        would_recommend=True,
    )
    assert feedback["success"] is True
    assert feedback["feedback"]["doctor_id"] == referred_card["feedback"]["target_doctor_id"]

    doctors = DoctorService.get_available_doctors()
    doctor_b_item = next(item for item in doctors if item["doctor_id"] == "doc-b")
    assert doctor_b_item["average_rating"] == 5.0
    assert doctor_b_item["review_count"] == 1
