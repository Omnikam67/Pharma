import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { ArrowRight, Calendar, CheckCircle, ClipboardPlus, Phone, User, Users, XCircle } from 'lucide-react';
import axios from 'axios';
import { API_BASE } from '../config/api';

const EMPTY_MEDICINE = {
  medicine_name: '',
  frequency: '',
  duration: '',
  notes: '',
};

export function AppointmentRequests({ doctorId, embedded = false, onStatusChange }) {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingSourceReferrals, setLoadingSourceReferrals] = useState(true);
  const [loadingTargetReferrals, setLoadingTargetReferrals] = useState(true);
  const [activeTab, setActiveTab] = useState('all');
  const [referralPanel, setReferralPanel] = useState('incoming');
  const [processingId, setProcessingId] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [sourceReferrals, setSourceReferrals] = useState([]);
  const [targetReferrals, setTargetReferrals] = useState([]);
  const [availableDoctors, setAvailableDoctors] = useState([]);
  const [cancelModal, setCancelModal] = useState({ open: false, appointmentId: null, reason: '' });
  const [referralModal, setReferralModal] = useState({
    open: false,
    appointment: null,
    to_doctor_id: '',
    reason: '',
    clinical_notes: '',
  });
  const [completionModal, setCompletionModal] = useState({
    open: false,
    appointment: null,
    prescription_notes: '',
    medicines: [{ ...EMPTY_MEDICINE }],
  });
  const [medicineSuggestions, setMedicineSuggestions] = useState({});

  const statusLabel = {
    all: 'All',
    pending: 'Pending',
    approved: 'Approved',
    completed: 'Completed',
    cancelled: 'Cancelled',
  };

  const getDisplayStatus = (appointment) => {
    if (
      appointment?.referral &&
      appointment.referral.from_doctor_id === doctorId &&
      appointment.referral.status === 'completed'
    ) {
      return 'completed';
    }
    return appointment.status;
  };

  const loadAppointments = useCallback(async () => {
    setLoading(true);
    try {
      if (activeTab === 'all') {
        const [pendingRes, approvedRes, completedRes, cancelledRes] = await Promise.all([
          axios.get(`${API_BASE}/doctor/appointments/pending/${doctorId}`),
          axios.get(`${API_BASE}/doctor/appointments/approved/${doctorId}`),
          axios.get(`${API_BASE}/doctor/appointments/completed/${doctorId}`),
          axios.get(`${API_BASE}/doctor/appointments/cancelled/${doctorId}`),
        ]);

        const allAppointments = [
          ...(pendingRes.data.appointments || []),
          ...(approvedRes.data.appointments || []),
          ...(completedRes.data.appointments || []),
          ...(cancelledRes.data.appointments || []),
        ].sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0));

        setAppointments(allAppointments);
      } else {
        const endpoint = `${API_BASE}/doctor/appointments/${activeTab}/${doctorId}`;
        const res = await axios.get(endpoint);
        setAppointments(res.data.appointments || []);
      }

      setError('');
    } catch (err) {
      console.error('Failed to load appointments:', err);
      setError('Failed to load appointments');
    } finally {
      setLoading(false);
    }
  }, [activeTab, doctorId]);

  useEffect(() => {
    loadAppointments();
  }, [loadAppointments]);

  const loadSourceReferrals = useCallback(async () => {
    setLoadingSourceReferrals(true);
    try {
      const res = await axios.get(`${API_BASE}/doctor/referrals/source/${doctorId}`);
      setSourceReferrals(res.data.referrals || []);
    } catch (err) {
      console.error('Failed to load referrals:', err);
    } finally {
      setLoadingSourceReferrals(false);
    }
  }, [doctorId]);

  useEffect(() => {
    loadSourceReferrals();
  }, [loadSourceReferrals]);

  const loadTargetReferrals = useCallback(async () => {
    setLoadingTargetReferrals(true);
    try {
      const res = await axios.get(`${API_BASE}/doctor/referrals/target/${doctorId}`);
      setTargetReferrals(res.data.referrals || []);
    } catch (err) {
      console.error('Failed to load incoming referrals:', err);
    } finally {
      setLoadingTargetReferrals(false);
    }
  }, [doctorId]);

  useEffect(() => {
    loadTargetReferrals();
  }, [loadTargetReferrals]);

  const loadAvailableDoctors = useCallback(async () => {
    try {
      const res = await axios.get(`${API_BASE}/doctor/available`);
      setAvailableDoctors((res.data.doctors || []).filter((doctor) => doctor.id !== doctorId));
    } catch (err) {
      console.error('Failed to load doctors for referral modal:', err);
    }
  }, [doctorId]);

  useEffect(() => {
    loadAvailableDoctors();
  }, [loadAvailableDoctors]);

  const handleApprove = async (appointmentId, enteredAmount) => {
    const revenueAmount = parseFloat(enteredAmount);
    if (Number.isNaN(revenueAmount) || revenueAmount < 0) {
      setError('Please enter a valid consultation fee');
      return;
    }

    setProcessingId(appointmentId);
    try {
      const res = await axios.post(`${API_BASE}/doctor/appointments/action`, {
        appointment_id: appointmentId,
        doctor_id: doctorId,
        action: 'approve',
        revenue_amount: revenueAmount,
      });

      if (!res.data.success) {
        setError(res.data.message || 'Failed to approve appointment');
        return;
      }

      await loadAppointments();
      await loadSourceReferrals();
      await loadTargetReferrals();
      setSuccess('Appointment approved successfully.');
      onStatusChange?.();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to approve appointment');
    } finally {
      setProcessingId(null);
    }
  };

  const handleCancel = async (appointmentId, reason) => {
    setProcessingId(appointmentId);
    try {
      const res = await axios.post(`${API_BASE}/doctor/appointments/action`, {
        appointment_id: appointmentId,
        doctor_id: doctorId,
        action: 'cancel',
        cancellation_reason: reason,
      });

      if (!res.data.success) {
        setError(res.data.message || 'Failed to cancel appointment');
        return;
      }

      await loadAppointments();
      await loadSourceReferrals();
      await loadTargetReferrals();
      setSuccess('Appointment cancelled successfully.');
      onStatusChange?.();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to cancel appointment');
    } finally {
      setProcessingId(null);
    }
  };

  const openCancelModal = (appointmentId) => {
    setCancelModal({ open: true, appointmentId, reason: '' });
    setError('');
  };

  const openCompletionModal = (appointment) => {
    setCompletionModal({
      open: true,
      appointment,
      prescription_notes: '',
      medicines: appointment.prescription_medicines?.length
        ? appointment.prescription_medicines
        : [{ ...EMPTY_MEDICINE }],
    });
    setMedicineSuggestions({});
    setError('');
  };

  const openReferralModal = (appointment) => {
    setReferralModal({
      open: true,
      appointment,
      to_doctor_id: '',
      reason: '',
      clinical_notes: appointment.notes || '',
    });
    setError('');
    setSuccess('');
  };

  const updateMedicineField = async (index, field, value) => {
    setCompletionModal((prev) => {
      const medicines = [...prev.medicines];
      medicines[index] = { ...medicines[index], [field]: value };
      return { ...prev, medicines };
    });

    if (field !== 'medicine_name') {
      return;
    }

    if (!value.trim()) {
      setMedicineSuggestions((prev) => ({ ...prev, [index]: [] }));
      return;
    }

    try {
      const res = await axios.get(`${API_BASE}/doctor/medicines/search`, {
        params: { prefix: value, limit: 8 },
      });
      setMedicineSuggestions((prev) => ({ ...prev, [index]: res.data.medicines || [] }));
    } catch (err) {
      console.error('Failed to fetch medicine suggestions', err);
    }
  };

  const selectSuggestion = (index, medicineName) => {
    setCompletionModal((prev) => {
      const medicines = [...prev.medicines];
      medicines[index] = { ...medicines[index], medicine_name: medicineName };
      return { ...prev, medicines };
    });
    setMedicineSuggestions((prev) => ({ ...prev, [index]: [] }));
  };

  const addMedicineRow = () => {
    setCompletionModal((prev) => ({
      ...prev,
      medicines: [...prev.medicines, { ...EMPTY_MEDICINE }],
    }));
  };

  const submitCompletion = async () => {
    const appointmentId = completionModal.appointment?.id;
    if (!appointmentId) {
      return;
    }

    const medicines = completionModal.medicines.filter((item) => item.medicine_name.trim());
    if (medicines.length === 0) {
      setError('Add at least one medicine before completing the appointment');
      return;
    }

    setProcessingId(appointmentId);
    try {
      const res = await axios.post(`${API_BASE}/doctor/appointments/complete`, {
        appointment_id: appointmentId,
        doctor_id: doctorId,
        prescription_notes: completionModal.prescription_notes || null,
        medicines,
      });

      if (!res.data.success) {
        setError(res.data.message || 'Failed to complete appointment');
        return;
      }

      setCompletionModal({
        open: false,
        appointment: null,
        prescription_notes: '',
        medicines: [{ ...EMPTY_MEDICINE }],
      });
      setMedicineSuggestions({});
      await loadAppointments();
      await loadSourceReferrals();
      await loadTargetReferrals();
      setSuccess('Appointment completed and prescription shared successfully.');
      onStatusChange?.();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to complete appointment');
    } finally {
      setProcessingId(null);
    }
  };

  const submitReferral = async () => {
    if (!referralModal.appointment?.id) {
      return;
    }
    if (!referralModal.to_doctor_id.trim()) {
      setError('Enter the doctor ID you want to refer this patient to');
      return;
    }
    if (!referralModal.reason.trim()) {
      setError('Referral reason is required');
      return;
    }

    setProcessingId(referralModal.appointment.id);
    try {
      const res = await axios.post(`${API_BASE}/doctor/referrals/create`, {
        source_appointment_id: referralModal.appointment.id,
        from_doctor_id: doctorId,
        to_doctor_id: referralModal.to_doctor_id.trim(),
        reason: referralModal.reason.trim(),
        clinical_notes: referralModal.clinical_notes.trim() || null,
      });
      if (!res.data.success) {
        setError(res.data.message || 'Failed to create referral');
        return;
      }

      setReferralModal({
        open: false,
        appointment: null,
        to_doctor_id: '',
        reason: '',
        clinical_notes: '',
      });
      await loadAppointments();
      await loadSourceReferrals();
      await loadTargetReferrals();
      setSuccess('Referral created successfully.');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create referral');
    } finally {
      setProcessingId(null);
    }
  };

  const AppointmentCard = ({ appointment }) => (
    <div className="bg-white border border-slate-200 rounded-xl p-5 hover:shadow-md transition">
      {(() => {
        const displayStatus = getDisplayStatus(appointment);

        return (
          <>
      <div className="flex items-center justify-between mb-4">
        <div className="flex flex-wrap items-center gap-2">
          <span
            className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ${
              displayStatus === 'completed'
                ? 'bg-emerald-100 text-emerald-700'
                : displayStatus === 'approved'
                ? 'bg-green-100 text-green-700'
                : displayStatus === 'cancelled'
                ? 'bg-red-100 text-red-700'
                : 'bg-yellow-100 text-yellow-700'
            }`}
          >
            {statusLabel[displayStatus] || 'Pending'}
          </span>
          {appointment.referral && (
            <span className="inline-flex items-center rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold text-blue-700">
              Referred by Dr. {appointment.referral.from_doctor_name || 'Doctor'}
            </span>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div className="flex items-center gap-3">
          <User size={20} className="text-blue-600" />
          <div>
            <p className="text-sm font-medium text-slate-600">Patient</p>
            <p className="font-bold text-slate-800">{appointment.patient_name}</p>
            <p className="text-sm text-slate-500">
              Age: {appointment.patient_age ?? 'N/A'} | Gender: {appointment.patient_gender || 'N/A'}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Phone size={20} className="text-green-600" />
          <div>
            <p className="text-sm font-medium text-slate-600">Contact</p>
            <p className="font-bold text-slate-800">{appointment.patient_phone}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4 pb-4 border-b border-slate-200">
        <div className="flex items-center gap-3">
          <Calendar size={20} className="text-violet-600" />
          <div>
            <p className="text-sm font-medium text-slate-600">Date</p>
            <p className="font-bold text-slate-800">{appointment.appointment_date || 'Not set'}</p>
          </div>
        </div>
        <div>
          <p className="text-sm font-medium text-slate-600">Time</p>
          <p className="font-bold text-slate-800">{appointment.appointment_time || 'Not set'}</p>
        </div>
      </div>

      {appointment.referral && (
        <div className="mb-4 rounded-lg border border-blue-100 bg-blue-50 p-3 text-sm text-blue-900">
          <p className="font-semibold">
            Referral: Dr. {appointment.referral.from_doctor_name || 'Doctor'} <ArrowRight size={14} className="inline mx-1" />
            Dr. {appointment.referral.to_doctor_name || 'Doctor'}
          </p>
          <p className="mt-1">Reason: {appointment.referral.reason}</p>
        </div>
      )}

      {displayStatus === 'pending' ? (
        <div className="flex gap-2">
          <button
            onClick={() => handleApprove(appointment.id, appointment.appointment_fee || '500')}
            disabled={processingId === appointment.id}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition disabled:opacity-50"
          >
            <CheckCircle size={18} /> Approve
          </button>
          <button
            onClick={() => openCancelModal(appointment.id)}
            disabled={processingId === appointment.id}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg font-semibold hover:bg-red-700 transition disabled:opacity-50"
          >
            <XCircle size={18} /> Cancel
          </button>
        </div>
      ) : displayStatus === 'approved' ? (
        <div className="flex gap-2">
          <div className="flex-1 rounded-lg bg-green-100 text-green-700 text-sm font-semibold text-center py-2">
            Confirmed with patient
          </div>
          {!appointment.referral_id && (
            <button
              onClick={() => openReferralModal(appointment)}
              className="flex items-center justify-center gap-2 rounded-lg bg-violet-600 px-4 py-2 text-sm font-semibold text-white hover:bg-violet-700 transition"
            >
              Refer
            </button>
          )}
          <button
            onClick={() => openCompletionModal(appointment)}
            className="flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 transition"
          >
            <ClipboardPlus size={16} /> Complete
          </button>
        </div>
      ) : (
        <div
          className={`p-2 rounded-lg text-sm font-semibold text-center ${
            displayStatus === 'completed'
              ? 'bg-emerald-100 text-emerald-700'
              : 'bg-red-100 text-red-700'
          }`}
        >
          {displayStatus === 'completed' ? 'Appointment completed' : 'Appointment cancelled'}
        </div>
      )}
          </>
        );
      })()}
    </div>
  );

  const incomingReferralSummary = useMemo(
    () => ({
      total: targetReferrals.length,
      pendingBooking: targetReferrals.filter((item) => item.status === 'pending_booking').length,
      booked: targetReferrals.filter((item) => item.status === 'booked').length,
    }),
    [targetReferrals]
  );

  const renderTargetReferrals = () => (
    <div className="app-panel mt-8 rounded-[28px] p-5">
      <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div>
          <p className="app-eyebrow">Incoming Referrals</p>
          <h3 className="mt-3 text-2xl font-black tracking-tight text-slate-900">Referral Requests</h3>
          <p className="mt-2 text-sm text-slate-600">
            See when another doctor refers a patient to you. The patient will also see this referral on their dashboard.
          </p>
        </div>
        <div className="grid grid-cols-3 gap-2 rounded-2xl border border-slate-200 bg-slate-50 p-3 text-center text-sm">
          <div>
            <p className="font-black text-slate-900">{incomingReferralSummary.total}</p>
            <p className="text-slate-500">Total</p>
          </div>
          <div>
            <p className="font-black text-amber-600">{incomingReferralSummary.pendingBooking}</p>
            <p className="text-slate-500">Waiting</p>
          </div>
          <div>
            <p className="font-black text-blue-600">{incomingReferralSummary.booked}</p>
            <p className="text-slate-500">Booked</p>
          </div>
        </div>
      </div>

      <div className="mt-4 space-y-4">
        {loadingTargetReferrals ? (
          <p className="text-slate-500">Loading referral requests...</p>
        ) : targetReferrals.length === 0 ? (
          <div className="rounded-xl border border-dashed border-slate-300 bg-white p-6 text-center text-slate-500">
            No doctors have referred patients to you yet.
          </div>
        ) : (
          targetReferrals.map((referral) => (
            <div key={referral.id} className="rounded-xl border border-slate-200 bg-white p-4">
              <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                <div className="space-y-2">
                  <p className="font-bold text-slate-900">
                    {referral.patient_name} was referred by Dr. {referral.from_doctor_name || 'Doctor'}
                  </p>
                  <p className="text-sm text-slate-600">
                    Patient phone: {referral.patient_phone} | Age: {referral.patient_age ?? 'N/A'} | Gender: {referral.patient_gender || 'N/A'}
                  </p>
                  <p className="text-sm text-slate-700">
                    Referral path: Dr. {referral.from_doctor_name || 'Doctor'} <ArrowRight size={14} className="inline mx-1" />
                    Dr. {referral.to_doctor_name || 'You'}
                  </p>
                  <p className="text-sm text-slate-600">Reason: {referral.reason}</p>
                  {referral.clinical_notes && (
                    <div className="rounded-lg border border-sky-100 bg-sky-50 p-3 text-sm text-slate-700">
                      <p className="font-semibold text-sky-700">Clinical notes from Dr. {referral.from_doctor_name || 'Doctor'}</p>
                      <p className="mt-1">{referral.clinical_notes}</p>
                    </div>
                  )}
                  {referral.status === 'pending_booking' && (
                    <p className="text-sm font-semibold text-amber-700">
                      Waiting for the patient to book with you.
                    </p>
                  )}
                  {referral.referred_appointment_status && (
                    <p className="text-sm font-semibold text-blue-700">
                      Appointment status on your side: {String(referral.referred_appointment_status).replace('_', ' ')}
                    </p>
                  )}
                </div>
                <div className="flex flex-col gap-2">
                  <span className="rounded-lg bg-blue-100 px-3 py-2 text-sm font-semibold text-blue-700 capitalize">
                    {String(referral.status || '').replace('_', ' ')}
                  </span>
                  {referral.result_appointment?.status === 'completed' && referral.result_appointment?.has_prescription_image && (
                    <a
                      href={`${API_BASE}/doctor/appointments/${referral.result_appointment.id}/prescription-download`}
                      target="_blank"
                      rel="noreferrer"
                      className="rounded-lg bg-blue-600 px-4 py-2 text-center text-sm font-semibold text-white hover:bg-blue-700 transition"
                    >
                      Download Prescription
                    </a>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );

  const renderSourceReferrals = () => (
    <div className="app-panel mt-8 rounded-[28px] p-5">
      <p className="app-eyebrow">Referral Oversight</p>
      <h3 className="mt-3 text-2xl font-black tracking-tight text-slate-900">Your Referrals</h3>
      <p className="mt-2 text-sm text-slate-600">
        Track patients you referred to specialists and review the final prescription in read-only mode.
      </p>

      <div className="mt-4 space-y-4">
        {loadingSourceReferrals ? (
          <p className="text-slate-500">Loading referrals...</p>
        ) : sourceReferrals.length === 0 ? (
          <div className="rounded-xl border border-dashed border-slate-300 bg-white p-6 text-center text-slate-500">
            No referrals created yet.
          </div>
        ) : (
          sourceReferrals.map((referral) => (
            <div key={referral.id} className="rounded-xl border border-slate-200 bg-white p-4">
              <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                <div className="space-y-2">
                  <p className="font-bold text-slate-900">
                    {referral.patient_name} | Dr. {referral.from_doctor_name || 'Doctor'} <ArrowRight size={14} className="inline mx-1" />
                    Dr. {referral.to_doctor_name || 'Doctor'}
                  </p>
                  <p className="text-sm text-slate-600">Reason: {referral.reason}</p>
                  {referral.clinical_notes && <p className="text-sm text-slate-700">Clinical notes: {referral.clinical_notes}</p>}
                  {referral.status === 'completed' && (
                    <p className="text-sm font-semibold text-emerald-700">
                      Referred case completed by Dr. {referral.to_doctor_name || 'Doctor'}
                    </p>
                  )}
                  {referral.result_appointment?.prescription_medicines?.length > 0 && (
                    <div className="rounded-lg border border-emerald-100 bg-emerald-50 p-3 text-sm text-emerald-900">
                      <p className="font-semibold text-emerald-800">Final Prescription</p>
                      {referral.result_appointment.prescription_medicines.map((medicine, index) => (
                        <p key={`${referral.id}-result-${index}`}>{index + 1}. {medicine.medicine_name}</p>
                      ))}
                    </div>
                  )}
                </div>
                <div className="flex flex-col gap-2">
                  <span className="rounded-lg bg-blue-100 px-3 py-2 text-sm font-semibold text-blue-700 capitalize">
                    {String(referral.status || '').replace('_', ' ')}
                  </span>
                  {referral.result_appointment?.status === 'completed' && referral.result_appointment?.has_prescription_image && (
                    <a
                      href={`${API_BASE}/doctor/appointments/${referral.result_appointment.id}/prescription-download`}
                      target="_blank"
                      rel="noreferrer"
                      className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 transition"
                    >
                      Download Prescription
                    </a>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );

  return (
    <div className={embedded ? '' : 'app-shell px-4 py-5 md:px-6'}>
      <div className={embedded ? '' : 'app-container'}>
        {!embedded && (
          <div className="app-hero mb-6 rounded-[30px] px-6 py-6">
            <p className="app-eyebrow">Clinical Queue</p>
            <h1 className="app-section-title mt-3">Appointment Requests</h1>
          </div>
        )}

        <div className="flex flex-wrap gap-3 mb-6">
          {['all', 'pending', 'approved', 'completed', 'cancelled'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`rounded-2xl px-5 py-2.5 text-sm font-semibold transition ${
                activeTab === tab ? 'app-btn-primary text-white' : 'app-btn-secondary text-slate-700'
              }`}
            >
              {statusLabel[tab]}
            </button>
          ))}
        </div>

        {error && <div className="mb-4 rounded-2xl border border-red-200 bg-red-50 p-4 text-red-700">{error}</div>}
        {success && <div className="mb-4 rounded-2xl border border-emerald-200 bg-emerald-50 p-4 text-emerald-700">{success}</div>}

        {loading ? (
          <div className="app-panel rounded-[28px] py-12 text-center text-slate-500">Loading...</div>
        ) : appointments.length === 0 ? (
          <div className="app-panel rounded-[28px] py-12 text-center text-slate-500">No {statusLabel[activeTab].toLowerCase()} appointments</div>
        ) : (
          <div className="grid gap-4">
            {appointments.map((apt) => (
              <AppointmentCard key={apt.id} appointment={apt} />
            ))}
          </div>
        )}

        <div className="mt-8 flex flex-wrap gap-3">
          <button
            onClick={() => setReferralPanel('incoming')}
            className={`inline-flex items-center gap-2 rounded-2xl px-5 py-3 text-sm font-semibold transition ${
              referralPanel === 'incoming' ? 'app-btn-primary text-white' : 'app-btn-secondary text-slate-700'
            }`}
          >
            <Users size={16} />
            Referral Requests
            {incomingReferralSummary.total > 0 && (
              <span className={`rounded-full px-2 py-0.5 text-xs font-bold ${referralPanel === 'incoming' ? 'bg-white/20 text-white' : 'bg-blue-100 text-blue-700'}`}>
                {incomingReferralSummary.total}
              </span>
            )}
          </button>
          <button
            onClick={() => setReferralPanel('outgoing')}
            className={`rounded-2xl px-5 py-3 text-sm font-semibold transition ${
              referralPanel === 'outgoing' ? 'app-btn-primary text-white' : 'app-btn-secondary text-slate-700'
            }`}
          >
            Your Referrals
          </button>
        </div>

        {referralPanel === 'incoming' ? renderTargetReferrals() : renderSourceReferrals()}

        {referralModal.open && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4">
            <div className="w-full max-w-xl rounded-2xl bg-white p-6 shadow-2xl">
              <h2 className="text-xl font-bold text-slate-900">Create Referral</h2>
              <p className="mt-2 text-sm text-slate-600">
                Refer this patient to another approved doctor. The patient will later book the referred consultation.
              </p>
              <div className="mt-4 space-y-4">
                <div>
                  <label className="mb-2 block text-sm font-medium text-slate-700">Enter doctor ID</label>
                  <input
                    type="text"
                    value={referralModal.to_doctor_id}
                    onChange={(e) => setReferralModal((prev) => ({ ...prev, to_doctor_id: e.target.value }))}
                    className="w-full rounded-lg border border-slate-300 px-4 py-3 outline-none focus:border-blue-500"
                    placeholder="Enter approved doctor ID"
                  />
                  <p className="mt-2 text-xs text-slate-500">
                    Enter the doctor ID directly. That doctor will see it under `Referral Requests`, and the patient will also see it on their dashboard.
                  </p>
                </div>
                <div>
                  <label className="mb-2 block text-sm font-medium text-slate-700">Reason</label>
                  <textarea
                    rows="3"
                    value={referralModal.reason}
                    onChange={(e) => setReferralModal((prev) => ({ ...prev, reason: e.target.value }))}
                    className="w-full rounded-lg border border-slate-300 px-4 py-3 outline-none focus:border-blue-500"
                    placeholder="Why are you referring this patient?"
                  />
                </div>
                <div>
                  <label className="mb-2 block text-sm font-medium text-slate-700">Clinical notes</label>
                  <textarea
                    rows="4"
                    value={referralModal.clinical_notes}
                    onChange={(e) => setReferralModal((prev) => ({ ...prev, clinical_notes: e.target.value }))}
                    className="w-full rounded-lg border border-slate-300 px-4 py-3 outline-none focus:border-blue-500"
                    placeholder="Short summary for the referred doctor"
                  />
                </div>
              </div>
              <div className="mt-5 flex justify-end gap-3">
                <button
                  onClick={() => setReferralModal({ open: false, appointment: null, to_doctor_id: '', reason: '', clinical_notes: '' })}
                  className="rounded-lg border border-slate-300 px-4 py-2 font-medium text-slate-700 hover:bg-slate-50"
                >
                  Back
                </button>
                <button
                  onClick={submitReferral}
                  disabled={processingId === referralModal.appointment?.id}
                  className="rounded-lg bg-violet-600 px-4 py-2 font-semibold text-white hover:bg-violet-700 disabled:opacity-50"
                >
                  Send Referral
                </button>
              </div>
            </div>
          </div>
        )}

        {cancelModal.open && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4">
            <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
              <h2 className="text-xl font-bold text-slate-900">Cancel Appointment</h2>
              <p className="mt-2 text-sm text-slate-600">Add an optional cancellation reason.</p>
              <textarea
                rows="4"
                value={cancelModal.reason}
                onChange={(e) => setCancelModal((prev) => ({ ...prev, reason: e.target.value }))}
                className="mt-4 w-full rounded-lg border border-slate-300 px-4 py-3 text-slate-900 outline-none focus:border-blue-500"
                placeholder="Reason for cancellation"
              />
              <div className="mt-5 flex justify-end gap-3">
                <button
                  onClick={() => setCancelModal({ open: false, appointmentId: null, reason: '' })}
                  className="rounded-lg border border-slate-300 px-4 py-2 font-medium text-slate-700 hover:bg-slate-50"
                >
                  Back
                </button>
                <button
                  onClick={() => handleCancel(cancelModal.appointmentId, cancelModal.reason)}
                  disabled={processingId === cancelModal.appointmentId}
                  className="rounded-lg bg-red-600 px-4 py-2 font-semibold text-white hover:bg-red-700 disabled:opacity-50"
                >
                  Confirm Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {completionModal.open && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4">
            <div className="w-full max-w-3xl rounded-2xl bg-white p-6 shadow-2xl max-h-[90vh] overflow-y-auto">
              <h2 className="text-2xl font-bold text-slate-900">Complete Appointment</h2>
              <p className="mt-2 text-sm text-slate-600">
                Add the prescription. When you complete this, the patient gets an appointment completed WhatsApp message and prescription summary.
              </p>

              <div className="mt-6 space-y-4">
                {completionModal.medicines.map((medicine, index) => (
                  <div key={`medicine-${index}`} className="rounded-xl border border-slate-200 p-4">
                    <div className="grid gap-4 md:grid-cols-2">
                      <div className="relative">
                        <label className="mb-2 block text-sm font-medium text-slate-700">Medicine name</label>
                        <input
                          type="text"
                          value={medicine.medicine_name}
                          onChange={(e) => updateMedicineField(index, 'medicine_name', e.target.value)}
                          placeholder="Start typing, like B..."
                          className="w-full rounded-lg border border-slate-300 px-4 py-3 outline-none focus:border-blue-500"
                        />
                        {medicineSuggestions[index]?.length > 0 && (
                          <div className="absolute z-10 mt-1 w-full rounded-lg border border-slate-200 bg-white shadow-lg">
                            {medicineSuggestions[index].map((item) => (
                              <button
                                key={`${index}-${item.product_id}`}
                                type="button"
                                onClick={() => selectSuggestion(index, item.product_name)}
                                className="block w-full px-4 py-2 text-left text-sm text-slate-700 hover:bg-slate-50"
                              >
                                {item.product_name}
                              </button>
                            ))}
                          </div>
                        )}
                      </div>

                      <div>
                        <label className="mb-2 block text-sm font-medium text-slate-700">Frequency</label>
                        <input
                          type="text"
                          value={medicine.frequency}
                          onChange={(e) => updateMedicineField(index, 'frequency', e.target.value)}
                          placeholder="Twice daily"
                          className="w-full rounded-lg border border-slate-300 px-4 py-3 outline-none focus:border-blue-500"
                        />
                      </div>
                      <div>
                        <label className="mb-2 block text-sm font-medium text-slate-700">Duration</label>
                        <input
                          type="text"
                          value={medicine.duration}
                          onChange={(e) => updateMedicineField(index, 'duration', e.target.value)}
                          placeholder="5 days"
                          className="w-full rounded-lg border border-slate-300 px-4 py-3 outline-none focus:border-blue-500"
                        />
                      </div>
                    </div>

                    <div className="mt-4">
                      <label className="mb-2 block text-sm font-medium text-slate-700">Extra note</label>
                      <input
                        type="text"
                        value={medicine.notes}
                        onChange={(e) => updateMedicineField(index, 'notes', e.target.value)}
                        placeholder="After food"
                        className="w-full rounded-lg border border-slate-300 px-4 py-3 outline-none focus:border-blue-500"
                      />
                    </div>
                  </div>
                ))}

                <button
                  type="button"
                  onClick={addMedicineRow}
                  className="rounded-lg border border-blue-200 px-4 py-2 text-sm font-semibold text-blue-700 hover:bg-blue-50"
                >
                  Add Another Medicine
                </button>

                <div>
                  <label className="mb-2 block text-sm font-medium text-slate-700">Prescription notes</label>
                  <textarea
                    rows="4"
                    value={completionModal.prescription_notes}
                    onChange={(e) =>
                      setCompletionModal((prev) => ({ ...prev, prescription_notes: e.target.value }))
                    }
                    placeholder="General advice or follow-up instructions"
                    className="w-full rounded-lg border border-slate-300 px-4 py-3 outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div className="mt-6 flex justify-end gap-3">
                <button
                  onClick={() =>
                    setCompletionModal({
                      open: false,
                      appointment: null,
                      prescription_notes: '',
                      medicines: [{ ...EMPTY_MEDICINE }],
                    })
                  }
                  className="rounded-lg border border-slate-300 px-4 py-2 font-medium text-slate-700 hover:bg-slate-50"
                >
                  Back
                </button>
                <button
                  onClick={submitCompletion}
                  disabled={processingId === completionModal.appointment?.id}
                  className="rounded-lg bg-blue-600 px-4 py-2 font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
                >
                  Complete Appointment
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
