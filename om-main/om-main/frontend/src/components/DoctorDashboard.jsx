import React, { useCallback, useEffect, useState } from 'react';
import { Calendar, CheckCircle, Clock, RefreshCw, TrendingUp } from 'lucide-react';
import axios from 'axios';
import { AppointmentRequests } from './AppointmentRequests';
import { API_BASE } from '../config/api';

export function DoctorDashboard({ doctorId, doctorName, onLogout, onOpenRevenue }) {
  const [stats, setStats] = useState({
    today_appointments: 0,
    today_revenue: 0,
    total_appointments: 0,
    total_revenue: 0,
    pending_requests: 0,
    approved_requests: 0,
    completed_requests: 0,
    cancelled_requests: 0,
    overall_filter: 'all',
  });
  const [loading, setLoading] = useState(true);

  const loadStats = useCallback(async (silent = false) => {
    if (!silent) setLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/doctor/dashboard/stats/${doctorId}`);
      setStats(res.data);
    } catch (err) {
      console.error('Failed to load stats:', err);
    } finally {
      if (!silent) setLoading(false);
    }
  }, [doctorId]);

  useEffect(() => {
    loadStats();
    const interval = setInterval(() => loadStats(true), 30000);
    return () => clearInterval(interval);
  }, [loadStats]);

  const StatBox = ({ label, value, icon, color = 'blue' }) => {
    const IconComponent = icon;
    const colorClasses = {
      blue: 'border-blue-100 text-blue-900',
      green: 'border-green-100 text-green-900',
      emerald: 'border-emerald-100 text-emerald-900',
      orange: 'border-amber-100 text-amber-900',
      red: 'border-rose-100 text-rose-900',
    };

    return (
      <div className={`app-metric rounded-[24px] p-5 ${colorClasses[color]}`}>
        <div className="flex items-center justify-between">
          <div>
            <p className="app-eyebrow opacity-80">{label}</p>
            <p className="mt-3 text-3xl font-black tracking-tight">{value}</p>
          </div>
          <div className="rounded-2xl bg-slate-50 p-3">
            <IconComponent size={26} className="opacity-70" />
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="app-shell px-4 py-5 md:px-6">
      <div className="app-container space-y-6">
        <header className="app-hero rounded-[30px] px-6 py-6 md:px-8">
          <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <p className="app-eyebrow">Clinical Workspace</p>
              <h1 className="app-section-title mt-3">Doctor Dashboard</h1>
              <p className="app-muted mt-2 text-sm md:text-base">Welcome, Dr. {doctorName}. Review appointments, referrals, and revenue performance from one place.</p>
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <button
                onClick={() => loadStats()}
                className="app-btn-secondary inline-flex items-center gap-2 rounded-2xl px-4 py-3 text-sm font-semibold"
              >
                <RefreshCw size={16} /> Refresh
              </button>
              {onOpenRevenue && (
                <button
                  onClick={onOpenRevenue}
                  className="app-btn-primary rounded-2xl px-5 py-3 text-sm font-semibold"
                >
                  Revenue Analysis
                </button>
              )}
              <button
                onClick={onLogout}
                className="rounded-2xl bg-slate-950 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
              >
                Logout
              </button>
            </div>
          </div>
        </header>

        {loading ? (
          <div className="app-panel rounded-[28px] py-16 text-center">
            <p className="app-muted">Loading dashboard...</p>
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-4 xl:grid-cols-5">
            <StatBox label="Pending" value={stats.pending_requests} icon={Clock} color="orange" />
            <StatBox label="Approved" value={stats.approved_requests} icon={CheckCircle} color="green" />
            <StatBox label="Completed" value={stats.completed_requests} icon={Calendar} color="emerald" />
            <StatBox label="Cancelled" value={stats.cancelled_requests} icon={Clock} color="red" />
            <StatBox
              label="Today's Revenue"
              value={`Rs ${Number(stats.today_revenue || 0).toFixed(2)}`}
              icon={TrendingUp}
              color="blue"
            />
          </div>
        )}

        <div className="app-panel rounded-[30px] p-5 md:p-6">
          <div className="mb-5 flex items-start justify-between gap-4">
            <div>
              <p className="app-eyebrow">Patient Flow</p>
              <h2 className="app-section-title mt-3 text-[1.8rem]">Appointment Requests</h2>
            </div>
          </div>
          <AppointmentRequests doctorId={doctorId} embedded onStatusChange={() => loadStats(true)} />
        </div>
      </div>
    </div>
  );
}
