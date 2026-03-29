import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  ArrowLeft,
  Calendar,
  CheckCircle,
  Clock,
  Download,
  DollarSign,
  MapPin,
  Phone,
  Stethoscope,
  XCircle,
} from 'lucide-react';
import axios from 'axios';
import { API_BASE } from '../config/api';

const FILTERS = ['all', 'pending', 'approved', 'completed', 'cancelled'];

export function AppointmentHistory({ patientPhone, onBack }) {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedFilter, setSelectedFilter] = useState('all');

  const loadAppointmentHistory = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const res = await axios.get(`${API_BASE}/doctor/appointment-history/${patientPhone}`);
      if (res.data.success) {
        setAppointments(res.data.appointments || []);
      } else {
        setError('Failed to load appointment history');
      }
    } catch (err) {
      console.error('Error loading history:', err);
      setError('Failed to load appointment history');
    } finally {
      setLoading(false);
    }
  }, [patientPhone]);

  useEffect(() => {
    loadAppointmentHistory();
  }, [loadAppointmentHistory]);

  const filteredAppointments =
    selectedFilter === 'all' ? appointments : appointments.filter((apt) => apt.status === selectedFilter);

  const counts = useMemo(
    () => ({
      total: appointments.length,
      approved: appointments.filter((item) => item.status === 'approved').length,
      completed: appointments.filter((item) => item.status === 'completed').length,
      pending: appointments.filter((item) => item.status === 'pending').length,
      cancelled: appointments.filter((item) => item.status === 'cancelled').length,
    }),
    [appointments]
  );

  const getStatusTone = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-emerald-100 text-emerald-700 border-emerald-200';
      case 'approved':
        return 'bg-green-100 text-green-700 border-green-200';
      case 'cancelled':
        return 'bg-rose-100 text-rose-700 border-rose-200';
      case 'pending':
        return 'bg-amber-100 text-amber-700 border-amber-200';
      default:
        return 'bg-slate-100 text-slate-700 border-slate-200';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <Calendar size={16} className="text-emerald-600" />;
      case 'approved':
        return <CheckCircle size={16} className="text-green-600" />;
      case 'cancelled':
        return <XCircle size={16} className="text-rose-600" />;
      default:
        return <Clock size={16} className="text-amber-600" />;
    }
  };

  return (
    <div className="app-shell px-4 py-5 md:px-6">
      <div className="app-container space-y-6">
        <div className="app-hero rounded-[30px] px-6 py-6">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <button
                onClick={onBack}
                className="mb-3 inline-flex items-center gap-2 rounded-xl bg-slate-950 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-800"
              >
                <ArrowLeft size={16} />
                Back
              </button>
              <p className="app-eyebrow">Patient Timeline</p>
              <h1 className="app-section-title mt-3">Appointment History</h1>
              <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
                Review consultation progress, prescriptions, and completed care in one place.
              </p>
            </div>
            <button
              onClick={loadAppointmentHistory}
              className="app-btn-secondary rounded-2xl px-4 py-3 text-sm font-semibold"
            >
              Refresh History
            </button>
          </div>
        </div>

        <section className="grid grid-cols-2 gap-3 lg:grid-cols-5">
          <div className="app-stat-card px-4 py-4">
            <p className="app-kicker">Total Visits</p>
            <p className="mt-3 text-3xl font-black tracking-tight text-blue-600">{counts.total}</p>
          </div>
          <div className="app-stat-card px-4 py-4">
            <p className="app-kicker">Approved</p>
            <p className="mt-3 text-3xl font-black tracking-tight text-green-600">{counts.approved}</p>
          </div>
          <div className="app-stat-card px-4 py-4">
            <p className="app-kicker">Completed</p>
            <p className="mt-3 text-3xl font-black tracking-tight text-emerald-600">{counts.completed}</p>
          </div>
          <div className="app-stat-card px-4 py-4">
            <p className="app-kicker">Pending</p>
            <p className="mt-3 text-3xl font-black tracking-tight text-amber-500">{counts.pending}</p>
          </div>
          <div className="app-stat-card px-4 py-4">
            <p className="app-kicker">Cancelled</p>
            <p className="mt-3 text-3xl font-black tracking-tight text-rose-600">{counts.cancelled}</p>
          </div>
        </section>

        <section className="app-soft-section p-5 md:p-6">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="app-kicker">Filters</p>
              <h2 className="mt-2 text-xl font-black tracking-tight text-slate-900">Care Journey</h2>
            </div>
            <div className="flex flex-wrap gap-2 rounded-2xl border border-slate-200 bg-white/80 p-2">
              {FILTERS.map((status) => (
                <button
                  key={status}
                  onClick={() => setSelectedFilter(status)}
                  className={`rounded-xl px-4 py-2 text-sm font-semibold capitalize transition ${
                    selectedFilter === status
                      ? 'bg-blue-600 text-white shadow-sm'
                      : 'text-slate-600 hover:bg-slate-100'
                  }`}
                >
                  {status}
                </button>
              ))}
            </div>
          </div>

          {error && (
            <div className="mt-5 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
              {error}
            </div>
          )}

          {loading ? (
            <div className="py-16 text-center text-slate-500">Loading appointment history...</div>
          ) : filteredAppointments.length === 0 ? (
            <div className="app-empty mt-6 rounded-[26px] p-10 text-center">
              <Calendar size={42} className="mx-auto mb-4 text-slate-300" />
              <p className="text-base font-medium">
                {appointments.length === 0 ? 'No appointments yet. Book your first consultation.' : 'No appointments found in this filter.'}
              </p>
            </div>
          ) : (
            <div className="mt-6 space-y-4">
              {filteredAppointments.map((appointment) => (
                <div key={appointment.id} className="app-list-card p-5 md:p-6">
                  <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
                    <div className="flex-1">
                      <div className="flex flex-wrap items-center gap-3">
                        <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-100 text-blue-600">
                          <Stethoscope size={22} />
                        </div>
                        <div>
                          <h3 className="text-xl font-black tracking-tight text-slate-900">
                            Dr. {appointment.doctor_name || 'Doctor'}
                          </h3>
                          <p className="mt-1 flex items-center gap-2 text-sm text-slate-600">
                            <MapPin size={15} />
                            {appointment.clinic_name || 'Clinic'}
                          </p>
                        </div>
                      </div>

                      <div className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                        <div className="rounded-2xl bg-slate-50 px-4 py-3">
                          <p className="app-kicker">Date</p>
                          <p className="mt-2 text-sm font-semibold text-slate-900">{appointment.appointment_date || 'Not set'}</p>
                        </div>
                        <div className="rounded-2xl bg-slate-50 px-4 py-3">
                          <p className="app-kicker">Time</p>
                          <p className="mt-2 text-sm font-semibold text-slate-900">{appointment.appointment_time || 'Not set'}</p>
                        </div>
                        <div className="rounded-2xl bg-slate-50 px-4 py-3">
                          <p className="app-kicker">Phone</p>
                          <p className="mt-2 flex items-center gap-2 text-sm font-semibold text-slate-900">
                            <Phone size={14} />
                            {appointment.patient_phone}
                          </p>
                        </div>
                        <div className="rounded-2xl bg-slate-50 px-4 py-3">
                          <p className="app-kicker">Consultation Fee</p>
                          <p className="mt-2 flex items-center gap-1 text-sm font-semibold text-slate-900">
                            <DollarSign size={14} />
                            Rs {appointment.appointment_fee || 'N/A'}
                          </p>
                        </div>
                      </div>

                      {appointment.notes && (
                        <div className="mt-4 rounded-2xl border border-blue-100 bg-blue-50/80 px-4 py-3">
                          <p className="app-kicker text-blue-500">Notes</p>
                          <p className="mt-2 text-sm leading-6 text-slate-700">{appointment.notes}</p>
                        </div>
                      )}

                      {appointment.prescription_medicines?.length > 0 && (
                        <div className="mt-4 rounded-2xl border border-emerald-100 bg-emerald-50/85 p-4">
                          <p className="app-kicker text-emerald-600">Prescription</p>
                          <div className="mt-3 space-y-2">
                            {appointment.prescription_medicines.map((medicine, index) => (
                              <div key={`${appointment.id}-${index}`} className="rounded-xl bg-white/80 px-3 py-2 text-sm font-medium text-emerald-950">
                                {index + 1}. {medicine.medicine_name}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {appointment.status === 'completed' && appointment.has_prescription_image && (
                        <a
                          href={`${API_BASE}/doctor/appointments/${appointment.id}/prescription-download`}
                          target="_blank"
                          rel="noreferrer"
                          className="mt-4 inline-flex items-center gap-2 rounded-2xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700"
                        >
                          <Download size={16} />
                          Download Prescription
                        </a>
                      )}
                    </div>

                    <div className="flex flex-col items-start gap-3 lg:items-end">
                      <span className={`app-pill ${getStatusTone(appointment.status)}`}>
                        {getStatusIcon(appointment.status)}
                        {appointment.status}
                      </span>
                      <div className="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-right text-xs text-slate-500">
                        <p className="app-kicker">Last Updated</p>
                        <p className="mt-2 text-sm font-semibold text-slate-800">
                          {appointment.updated_at ? new Date(appointment.updated_at).toLocaleString() : 'Not available'}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
