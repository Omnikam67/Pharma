import React, { useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';
import axios from 'axios';
import { API_BASE } from '../config/api';

export function DoctorRegistration({ onBack, onSuccess }) {
  const [formData, setFormData] = useState({
    doctor_id: '',
    name: '',
    email: '',
    phone: '',
    specialty: '',
    gender: '',
    experience_years: '',
    qualification: '',
    hospital_name: '',
    address: '',
    appointment_fee: '',
    password: '',
    confirmPassword: '',
    profile_image: '',
    degree_certificate_image: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleFileChange = (e) => {
    const { name, files } = e.target;
    const file = files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      setFormData((prev) => ({ ...prev, [name]: reader.result }));
    };
    reader.readAsDataURL(file);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    const requiredFields = [
      ['doctor_id', 'Doctor ID'],
      ['name', 'Name'],
      ['email', 'Email'],
      ['phone', 'Phone number'],
      ['specialty', 'Specialist'],
      ['gender', 'Gender'],
      ['experience_years', 'Experience'],
      ['qualification', 'Qualification'],
      ['hospital_name', 'Hospital name'],
      ['address', 'Address'],
      ['appointment_fee', 'Fees'],
      ['password', 'Password'],
    ];

    for (const [key, label] of requiredFields) {
      if (!String(formData[key] || '').trim()) {
        setError(`${label} is required`);
        return;
      }
    }

    if (!formData.profile_image) {
      setError('Doctor image is required');
      return;
    }
    if (!formData.degree_certificate_image) {
      setError('Degree certificate image is required');
      return;
    }
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    setLoading(true);

    try {
      const res = await axios.post(`${API_BASE}/doctor/register`, {
        doctor_id: formData.doctor_id,
        name: formData.name,
        email: formData.email,
        phone: formData.phone,
        specialty: formData.specialty,
        gender: formData.gender,
        experience_years: parseInt(formData.experience_years, 10) || 0,
        qualification: formData.qualification,
        hospital_name: formData.hospital_name,
        address: formData.address,
        appointment_fee: parseFloat(formData.appointment_fee) || 0,
        password: formData.password,
        profile_image: formData.profile_image,
        degree_certificate_image: formData.degree_certificate_image,
        preferred_language: 'en',
      });

      if (res.data.success) {
        setSuccess('Registration successful! Your doctor account is pending system manager approval.');
        setTimeout(() => {
          if (onSuccess) onSuccess();
          if (onBack) onBack();
        }, 1500);
      } else {
        setError(res.data.message || 'Registration failed');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const fields = [
    ['doctor_id', 'Doctor ID', 'text'],
    ['name', 'Doctor Name', 'text'],
    ['email', 'Email', 'email'],
    ['phone', 'Phone Number', 'tel'],
    ['specialty', 'Specialist', 'text'],
    ['experience_years', 'Experience (Years)', 'number'],
    ['qualification', 'Qualification', 'text'],
    ['hospital_name', 'Hospital Name', 'text'],
    ['appointment_fee', 'Fees', 'number'],
  ];

  return (
    <div className="app-shell px-4 py-5 md:px-6">
      <div className="mx-auto max-w-3xl">
        <div className="app-hero rounded-[30px] px-6 py-6 md:px-8">
          <button onClick={onBack} className="mb-4 inline-flex items-center rounded-2xl bg-slate-950 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-800">
            Back
          </button>
          <p className="app-eyebrow">Provider Onboarding</p>
          <h1 className="app-section-title mt-3">Doctor Registration</h1>
          <p className="app-muted mt-2 max-w-2xl text-sm md:text-base">
            Register your professional profile, upload credentials, and submit your account for approval.
          </p>
        </div>

        <div className="app-panel mt-6 rounded-[30px] p-6 md:p-8">
          {error && <div className="mb-4 rounded-2xl border border-red-200 bg-red-50 p-4 text-red-700">{error}</div>}
          {success && <div className="mb-4 rounded-2xl border border-emerald-200 bg-emerald-50 p-4 text-emerald-700">{success}</div>}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="grid gap-5 md:grid-cols-2">
            {fields.map(([name, label, type]) => (
              <div key={name}>
                <label className="mb-2 block text-sm font-semibold text-slate-700">{label} *</label>
                <input
                  type={type}
                  name={name}
                  value={formData[name]}
                  onChange={handleInputChange}
                  className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            ))}
            </div>

            <div>
              <label className="mb-2 block text-sm font-semibold text-slate-700">Gender *</label>
              <select
                name="gender"
                value={formData.gender}
                onChange={handleInputChange}
                className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select gender</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div>
              <label className="mb-2 block text-sm font-semibold text-slate-700">Address *</label>
              <textarea
                name="address"
                value={formData.address}
                onChange={handleInputChange}
                rows="3"
                className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div className="grid gap-5 md:grid-cols-2">
              <div>
                <label className="mb-2 block text-sm font-semibold text-slate-700">Doctor Image *</label>
                <input type="file" name="profile_image" accept="image/*" onChange={handleFileChange} className="w-full rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-4 py-3" />
              </div>

              <div>
                <label className="mb-2 block text-sm font-semibold text-slate-700">Degree Certificate Image *</label>
                <input type="file" name="degree_certificate_image" accept="image/*" onChange={handleFileChange} className="w-full rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-4 py-3" />
              </div>
            </div>

            <div className="grid gap-5 md:grid-cols-2">
            <div>
              <label className="mb-2 block text-sm font-semibold text-slate-700">Password *</label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 pr-10 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 shadow-none">
                  {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
            </div>

            <div>
              <label className="mb-2 block text-sm font-semibold text-slate-700">Confirm Password *</label>
              <div className="relative">
                <input
                  type={showConfirmPassword ? 'text' : 'password'}
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                  className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 pr-10 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button type="button" onClick={() => setShowConfirmPassword(!showConfirmPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 shadow-none">
                  {showConfirmPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
            </div>
            </div>

            <button type="submit" disabled={loading} className="app-btn-primary mt-2 w-full rounded-2xl px-6 py-3.5 text-sm font-semibold text-white disabled:opacity-60">
              {loading ? 'Registering...' : 'Register as Doctor'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
