import { useEffect, useMemo, useState } from "react";
import axios from "axios";
import { Loader2, MapPin, Package, Phone, ShieldCheck, Truck, User, XCircle } from "lucide-react";
import { API_BASE } from "../config/api";

export function DeliveryBoyDashboard({ deliveryBoy, onLogout }) {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("pending");
  const [otpInputs, setOtpInputs] = useState({});
  const [otpFeedback, setOtpFeedback] = useState({});
  const [cancelModal, setCancelModal] = useState({ open: false, orderId: null, reason: "" });
  const [processingOrderId, setProcessingOrderId] = useState(null);
  const [error, setError] = useState("");

  const loadOrders = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await axios.get(`${API_BASE}/delivery/orders/${deliveryBoy?.id}`, {
        params: { status: activeTab === "all" ? undefined : activeTab },
      });
      setOrders(res.data?.orders || []);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Failed to load delivery orders");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!deliveryBoy?.id) return;
    loadOrders();
  }, [deliveryBoy?.id, activeTab]);

  const counts = useMemo(() => {
    const summary = { pending: 0, completed: 0, cancelled: 0 };
    orders.forEach((order) => {
      const status = String(order.status || "").toLowerCase();
      if (summary[status] !== undefined) summary[status] += 1;
    });
    return summary;
  }, [orders]);

  const handleComplete = async (orderId) => {
    const otp = String(otpInputs[orderId] || "").trim();
    if (!/^\d{6}$/.test(otp)) {
      setOtpFeedback((prev) => ({
        ...prev,
        [orderId]: { type: "error", message: "Please enter a valid 6-digit OTP." },
      }));
      return;
    }

    setProcessingOrderId(orderId);
    setError("");
    setOtpFeedback((prev) => ({ ...prev, [orderId]: { type: "", message: "" } }));
    try {
      await axios.post(`${API_BASE}/delivery/orders/${orderId}/complete`, {
        delivery_boy_id: deliveryBoy.id,
        otp,
      });
      setOtpInputs((prev) => ({ ...prev, [orderId]: "" }));
      setActiveTab("completed");
    } catch (err) {
      const message = err.response?.data?.detail || err.message || "Enter valid OTP sent on WhatsApp.";
      setOtpFeedback((prev) => ({
        ...prev,
        [orderId]: {
          type: "error",
          message: message === "Invalid OTP" ? "Enter valid OTP sent on WhatsApp." : message,
        },
      }));
    } finally {
      setProcessingOrderId(null);
      loadOrders();
    }
  };

  const openCancelModal = (orderId) => {
    setCancelModal({ open: true, orderId, reason: "" });
    setError("");
  };

  const submitCancel = async () => {
    if (!cancelModal.reason.trim()) {
      setError("Cancellation reason is required.");
      return;
    }
    setProcessingOrderId(cancelModal.orderId);
    setError("");
    try {
      const res = await axios.post(`${API_BASE}/delivery/orders/${cancelModal.orderId}/cancel`, {
        delivery_boy_id: deliveryBoy.id,
        reason: cancelModal.reason.trim(),
      });
      if (!res.data?.success) {
        setError(res.data?.message || "Failed to cancel order");
      }
      setCancelModal({ open: false, orderId: null, reason: "" });
      await loadOrders();
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Failed to cancel order");
    } finally {
      setProcessingOrderId(null);
    }
  };

  const statusTone = (status) => {
    if (status === "completed") return "bg-emerald-100 text-emerald-700";
    if (status === "cancelled") return "bg-rose-100 text-rose-700";
    return "bg-amber-100 text-amber-700";
  };

  return (
    <div className="app-shell px-4 py-5 md:px-6">
      <div className="app-container space-y-6">
        <header className="app-hero rounded-[30px] px-6 py-6">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <p className="app-eyebrow">Fulfilment Desk</p>
              <h1 className="app-section-title mt-3">{deliveryBoy?.name || "Delivery Partner"}</h1>
              <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
                Manage assigned deliveries, verify customer OTPs, and close each order with a clean audit trail.
              </p>
            </div>
            <button
              onClick={onLogout}
              className="rounded-2xl bg-rose-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-rose-700"
            >
              Logout
            </button>
          </div>
        </header>

        <section className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div className="app-stat-card px-5 py-5">
            <p className="app-kicker">Pending Runs</p>
            <p className="mt-3 text-3xl font-black tracking-tight text-amber-500">{counts.pending}</p>
          </div>
          <div className="app-stat-card px-5 py-5">
            <p className="app-kicker">Completed Today</p>
            <p className="mt-3 text-3xl font-black tracking-tight text-emerald-600">{counts.completed}</p>
          </div>
          <div className="app-stat-card px-5 py-5">
            <p className="app-kicker">Cancelled</p>
            <p className="mt-3 text-3xl font-black tracking-tight text-rose-600">{counts.cancelled}</p>
          </div>
        </section>

        <section className="app-soft-section p-5 md:p-6">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <p className="app-kicker">Task Queue</p>
              <h2 className="mt-2 text-xl font-black tracking-tight text-slate-900">Assigned Orders</h2>
            </div>
            <div className="flex flex-wrap gap-2">
              {["pending", "completed", "cancelled"].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`rounded-full px-4 py-2 text-sm font-semibold capitalize transition ${
                    activeTab === tab ? "bg-blue-600 text-white" : "bg-white text-slate-700 hover:bg-slate-100"
                  }`}
                >
                  {tab}
                </button>
              ))}
              <button
                onClick={loadOrders}
                className="rounded-2xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-800"
              >
                Refresh
              </button>
            </div>
          </div>

          {error && (
            <div className="mt-5 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
              {error}
            </div>
          )}

          {loading ? (
            <div className="flex justify-center py-16">
              <Loader2 size={32} className="animate-spin text-blue-600" />
            </div>
          ) : orders.length === 0 ? (
            <div className="app-empty mt-6 rounded-[26px] p-10 text-center">
              No {activeTab} orders available right now.
            </div>
          ) : (
            <div className="mt-6 grid gap-4">
              {orders.map((order) => (
                <div key={order.order_id} className="app-list-card p-5 md:p-6">
                  <div className="flex flex-col gap-5 xl:flex-row xl:items-start xl:justify-between">
                    <div className="flex-1">
                      <div className="flex flex-wrap items-center gap-3">
                        <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-100 text-blue-600">
                          <Package size={22} />
                        </div>
                        <div>
                          <h3 className="text-xl font-black tracking-tight text-slate-900">{order.medicine}</h3>
                          <p className="mt-1 text-sm text-slate-600">Quantity: {order.quantity} units</p>
                        </div>
                      </div>

                      <div className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
                        <div className="rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-700">
                          <p className="app-kicker">Customer</p>
                          <p className="mt-2 flex items-center gap-2 font-semibold text-slate-900">
                            <User size={15} />
                            {order.customer_name}
                          </p>
                        </div>
                        <div className="rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-700">
                          <p className="app-kicker">Phone</p>
                          <p className="mt-2 flex items-center gap-2 font-semibold text-slate-900">
                            <Phone size={15} />
                            {order.customer_phone || "N/A"}
                          </p>
                        </div>
                        <div className="rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-700">
                          <p className="app-kicker">Route</p>
                          <div className="mt-2 flex items-start gap-2 text-slate-900">
                            <MapPin size={15} className="mt-0.5 text-rose-500" />
                            <div>
                              <p className="font-semibold">{order.delivery_location || "No delivery location"}</p>
                              {order.delivery_map_url && (
                                <a href={order.delivery_map_url} target="_blank" rel="noreferrer" className="mt-1 inline-block text-sm font-semibold text-blue-600 hover:underline">
                                  Open map
                                </a>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="w-full max-w-sm rounded-[24px] border border-slate-200 bg-white p-4">
                      <div className="flex items-center justify-between">
                        <span className={`rounded-full px-3 py-1 text-xs font-bold uppercase ${statusTone(order.status)}`}>
                          {String(order.status || "").toUpperCase()}
                        </span>
                        <div className="flex items-center gap-2 text-xs font-semibold text-slate-500">
                          <Truck size={14} />
                          Assigned delivery
                        </div>
                      </div>

                      {activeTab === "pending" ? (
                        <div className="mt-4 space-y-3">
                          <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3">
                            <label className="app-kicker">Customer OTP</label>
                            <input
                              type="text"
                              maxLength={6}
                              value={otpInputs[order.order_id] || ""}
                              onChange={(e) => {
                                const cleanOtp = e.target.value.replace(/\D/g, "").slice(0, 6);
                                setOtpInputs((prev) => ({ ...prev, [order.order_id]: cleanOtp }));
                                setOtpFeedback((prev) => ({
                                  ...prev,
                                  [order.order_id]: { type: "", message: "" },
                                }));
                              }}
                              placeholder="Enter 6-digit OTP"
                              className="mt-3 w-full rounded-xl border border-slate-300 px-4 py-3"
                            />
                            {otpFeedback[order.order_id]?.message && (
                              <div
                                className={`mt-3 rounded-xl px-3 py-2 text-sm ${
                                  otpFeedback[order.order_id].type === "success"
                                    ? "border border-emerald-200 bg-emerald-50 text-emerald-700"
                                    : "border border-rose-200 bg-rose-50 text-rose-700"
                                }`}
                              >
                                {otpFeedback[order.order_id].message}
                              </div>
                            )}
                          </div>

                          <div className="grid grid-cols-2 gap-3">
                            <button
                              onClick={() => handleComplete(order.order_id)}
                              disabled={processingOrderId === order.order_id}
                              className="rounded-2xl bg-emerald-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:opacity-60"
                            >
                              {processingOrderId === order.order_id ? "Completing..." : "Complete Delivery"}
                            </button>
                            <button
                              onClick={() => openCancelModal(order.order_id)}
                              disabled={processingOrderId === order.order_id}
                              className="rounded-2xl bg-rose-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-rose-700 disabled:opacity-60"
                            >
                              Cancel
                            </button>
                          </div>

                          <div className="flex items-center gap-2 rounded-2xl border border-sky-100 bg-sky-50 px-3 py-3 text-sm text-sky-800">
                            <ShieldCheck size={16} />
                            Complete the order only after OTP verification from the customer.
                          </div>
                        </div>
                      ) : (
                        <div className="mt-4 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4 text-sm text-slate-700">
                          <div className="flex items-center gap-2 font-semibold text-slate-900">
                            {order.status === "cancelled" ? <XCircle size={16} className="text-rose-600" /> : <ShieldCheck size={16} className="text-emerald-600" />}
                            {order.status === "cancelled" ? "Delivery closed as cancelled" : "Delivery verified and completed"}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {cancelModal.open && (
          <div className="fixed inset-0 z-40 flex items-center justify-center bg-slate-950/45 px-4 backdrop-blur-sm">
            <div className="w-full max-w-md rounded-[28px] border border-slate-200 bg-white p-6 shadow-2xl">
              <p className="app-kicker">Cancellation Reason</p>
              <h3 className="mt-2 text-2xl font-black tracking-tight text-slate-900">Cancel Delivery</h3>
              <p className="mt-2 text-sm text-slate-600">
                Add a clear reason so the support team and customer can understand what happened.
              </p>
              <textarea
                rows={4}
                value={cancelModal.reason}
                onChange={(e) => setCancelModal((prev) => ({ ...prev, reason: e.target.value }))}
                className="mt-4 w-full rounded-2xl border border-slate-300 px-4 py-3"
                placeholder="Driver unavailable, incorrect address, customer unreachable..."
              />
              <div className="mt-5 flex justify-end gap-3">
                <button
                  onClick={() => setCancelModal({ open: false, orderId: null, reason: "" })}
                  className="rounded-2xl border border-slate-300 px-4 py-2.5 text-sm font-semibold text-slate-700"
                >
                  Close
                </button>
                <button
                  onClick={submitCancel}
                  disabled={processingOrderId === cancelModal.orderId}
                  className="rounded-2xl bg-rose-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-rose-700 disabled:opacity-60"
                >
                  {processingOrderId === cancelModal.orderId ? "Submitting..." : "Confirm Cancel"}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
