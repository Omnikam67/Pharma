import React, { useState, useEffect } from 'react';
import { TrendingUp, DollarSign, Calendar, Users } from 'lucide-react';
import axios from 'axios';
import { API_BASE } from '../config/api';

export function RevenueAnalytics({ doctorId, onBack }) {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState('today');
  const [error, setError] = useState('');

  useEffect(() => {
    loadAnalytics();
  }, [doctorId, selectedPeriod]);

  const loadAnalytics = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/doctor/revenue/${doctorId}?filter_type=${selectedPeriod}`);
      setAnalytics(res.data);
      setError('');
    } catch (err) {
      console.error('Failed to load analytics:', err);
      setError('Failed to load revenue analytics');
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ label, value, icon, color }) => {
    const IconComponent = icon;
    const colorClasses = {
      green: 'border-green-100 text-green-900',
      blue: 'border-blue-100 text-blue-900',
      purple: 'border-cyan-100 text-cyan-900',
      orange: 'border-amber-100 text-amber-900'
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

  const breakdownRows = analytics?.daily_breakdown
    ? Object.entries(analytics.daily_breakdown).sort(([a], [b]) => (a > b ? -1 : 1))
    : [];

  return (
    <div className="app-shell px-4 py-5 md:px-6">
      <div className="app-container">
        <div className="app-hero mb-6 rounded-[30px] px-6 py-6 md:px-8">
          <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
            <div>
            {onBack && (
              <button
                onClick={onBack}
                className="mb-3 inline-flex items-center rounded-2xl bg-slate-950 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-800"
              >
                Back to Dashboard
              </button>
            )}
              <p className="app-eyebrow">Business Overview</p>
              <h1 className="app-section-title mt-3">Revenue Analysis</h1>
              <p className="app-muted mt-2 max-w-2xl text-sm md:text-base">Monitor appointment conversion, cancellations, and earnings with a cleaner analytics view.</p>
            </div>

          <div className="flex flex-wrap gap-2">
            {[
              { value: 'today', label: 'Today' },
              { value: 'previous_day', label: 'Previous Day' },
              { value: 'week', label: 'Last 7 Days' },
              { value: 'previous_week', label: 'Previous Week' },
              { value: 'month', label: 'This Month' },
              { value: 'all', label: 'All-Time' }
            ].map(period => (
              <button
                key={period.value}
                onClick={() => setSelectedPeriod(period.value)}
                className={`rounded-2xl px-4 py-2.5 text-sm font-semibold transition ${
                  selectedPeriod === period.value
                    ? 'app-btn-primary text-white'
                    : 'app-btn-secondary text-slate-700'
                }`}
              >
                {period.label}
              </button>
            ))}
          </div>
        </div>
        </div>

        {error && (
          <div className="mb-4 rounded-2xl border border-red-200 bg-red-50 p-4 text-red-700">
            {error}
          </div>
        )}

        {loading ? (
          <div className="app-panel rounded-[28px] py-16 text-center text-slate-500">Loading analytics...</div>
        ) : analytics ? (
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
              <StatCard
                label="Total Revenue"
                value={`Rs ${Number(analytics.total_revenue || 0).toFixed(2)}`}
                icon={DollarSign}
                color="green"
              />
              <StatCard
                label="Total Appointments"
                value={analytics.total_appointments}
                icon={Users}
                color="blue"
              />
              <StatCard
                label="Approved"
                value={analytics.approved_appointments}
                icon={TrendingUp}
                color="purple"
              />
              <StatCard
                label="Cancelled"
                value={analytics.cancelled_appointments}
                icon={Calendar}
                color="orange"
              />
            </div>

            <div className="app-panel rounded-[28px] p-6">
              <h2 className="text-xl font-black tracking-tight text-slate-900">Performance Summary</h2>

              <div className="mt-5 space-y-4">
                <div className="flex items-center justify-between rounded-2xl bg-slate-50 p-4">
                  <span className="text-slate-700 font-medium">Average Revenue per Approved Appointment</span>
                  <span className="text-2xl font-bold text-green-600">
                    Rs {analytics.approved_appointments > 0
                      ? (analytics.total_revenue / analytics.approved_appointments).toFixed(2)
                      : '0.00'}
                  </span>
                </div>

                <div className="flex items-center justify-between rounded-2xl bg-slate-50 p-4">
                  <span className="text-slate-700 font-medium">Approval Rate</span>
                  <span className="text-2xl font-bold text-blue-600">
                    {analytics.total_appointments > 0
                      ? ((analytics.approved_appointments / analytics.total_appointments) * 100).toFixed(1)
                      : '0'}%
                  </span>
                </div>

                <div className="flex items-center justify-between rounded-2xl bg-slate-50 p-4">
                  <span className="text-slate-700 font-medium">Pending Approvals</span>
                  <span className="text-2xl font-bold text-yellow-600">{analytics.pending_appointments || 0}</span>
                </div>
              </div>
            </div>

            <div className="app-panel rounded-[28px] p-6">
              <h2 className="text-xl font-black tracking-tight text-slate-900">Revenue by Day</h2>
              {breakdownRows.length === 0 ? (
                <p className="mt-4 text-slate-500">No revenue records found for this filter.</p>
              ) : (
                <div className="mt-5 space-y-3">
                  {breakdownRows.map(([day, amount]) => (
                    <div key={day} className="flex items-center justify-between rounded-2xl border border-slate-100 bg-slate-50 p-3">
                      <span className="font-medium text-slate-700">{day}</span>
                      <span className="font-bold text-emerald-700">Rs {Number(amount).toFixed(2)}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}
