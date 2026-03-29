  import { useState, useEffect, useRef, useCallback } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import { io } from "socket.io-client";
import "./App.css";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";
import { 
  Send, Mic, Bell, Pill, User, Bot, Trash2, 
  Loader2, PlusCircle, History, ArrowLeft, Calendar, Package,
  Paperclip, Edit2, Search, X, Save, Phone, UserCircle, Clock, Map,
  ShoppingCart, MenuIcon, LogOut, Home, Camera, Lock, Eye, EyeOff, Sun, Moon, BarChart3, TrendingUp, Users
} from "lucide-react";

// ==========================================
// CONFIGURATION & CONSTANTS
// ==========================================
const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
const SOCKET_URL = API_BASE;

// Medical theme colors
const COLORS = {
  primary: "#0ea5a4",    // Teal (medical trust)
  secondary: "#38bdf8",  // Sky blue
  accent: "#10b981",     // Emerald (health)
  danger: "#ef4444",     // Red
  muted: "#64748b",      // Slate gray
};

const I18N = {
  en: {
    app_name: "Pharma AI",
    choose_role: "Choose how you want to proceed",
    continue: "Continue",
    user_chatbot: "User (chatbot)",
    admin_inventory: "Admin (inventory)",
    login_as: "Login as {role}",
    register_as: "Register as {role}",
    login: "Login",
    register: "Register",
    name: "Name",
    phone_number: "Phone number",
    age: "Age",
    shop_id: "Shop ID",
    password: "Password",
    name_required: "Name is required",
    shop_id_required: "Shop ID is required",
    phone_required: "Phone number is required",
    password_required: "Password is required",
    processing: "Processing...",
    already_have_account: "Already have an account? Login",
    dont_have_account: "Don't have an account? Register",
    dashboard: "Dashboard",
    products: "Products",
    chat: "Chat",
    orders: "Orders",
    history: "History",
    light: "Light",
    dark: "Dark",
    profile: "Profile",
    welcome_back: "Welcome back, {name}",
    chat_title: "AI Health Assistant",
    chat_subtitle: "Ask me anything about your medications",
    shop_products: "Browse Medicines",
    shop_subtitle: "Find the medicines you need",
    all_products: "Available Products",
    all_products_subtitle: "Search and filter our complete medicine catalog",
    search_products: "Search medicines...",
    order_now: "Order Now",
    nearby_shops: "Nearby Pharmacies",
    nearby_title: "Find Pharmacies Near You",
    nearby_subtitle: "Locate and get medicines from nearby shops",
    use_location: "Use My Location",
    distance: "Distance",
    open_map: "Open Map",
    clear_chat: "Clear Chat",
    consulting_db: "Consulting database...",
    listening_placeholder: "Listening...",
    input_placeholder: "How can I help you today?",
    refill_alerts: "Refill Alerts",
    order_paracetamol: "Order Paracetamol",
    order_paracetamol_command: "Order me paracetamol 500mg",
    cancel_order: "Cancel Order",
    cancelling: "Cancelling...",
    close: "Close",
    save: "Save",
    logout: "Logout",
    profile_title: "Your Profile",
    language: "Language",
  },
  hi: {
    // Hindi translations (same structure)...
  },
  mr: {
    // Marathi translations (same structure)...
  },
};

// ==========================================
// UTILITY FUNCTIONS
// ==========================================
const getI18n = (lang = "en") => {
  return (key, vars = {}) => {
    const str = (I18N[lang] && I18N[lang][key]) || I18N.en[key] || key;
    return Object.keys(vars).reduce((acc, k) => acc.replaceAll(`{${k}}`, vars[k]), str);
  };
};

// Fix Leaflet marker icon issue
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

// ==========================================
// REUSABLE LAYOUT COMPONENT (DRY PRINCIPLE)
// ==========================================
function UserLayout({ children, isDarkMode, setIsDarkMode, onProfileClick, view, onNavigate, currentUser }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const t = getI18n("en");

  const NavigationItem = ({ icon: Icon, label, viewId }) => (
    <button
      onClick={() => {
        onNavigate(viewId);
        setMobileMenuOpen(false);
      }}
      className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition
        ${view === viewId
          ? "bg-teal-500/20 text-teal-600 dark:text-teal-300"
          : "hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300"
        }`}
    >
      <Icon size={20} />
      <span>{label}</span>
    </button>
  );

  return (
    <div className={`flex h-screen ${isDarkMode ? "bg-gray-900" : "bg-gray-50"}`}>
      {/* SIDEBAR - ALWAYS FIXED */}
      <aside className={`w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 transition-all
        ${mobileMenuOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"} 
        fixed left-0 top-0 h-screen z-40 overflow-y-auto`}>
        
        {/* Close button on mobile */}
        <button
          onClick={() => setMobileMenuOpen(false)}
          className="md:hidden absolute top-4 right-4 p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
        >
          <X size={24} />
        </button>

        {/* Logo */}
        <div className="p-6 border-b border-gray-200 dark:border-gray-700 flex items-center gap-3">
          <div className="w-10 h-10 bg-teal-500 rounded-lg flex items-center justify-center">
            <Pill className="text-white" size={24} />
          </div>
          <div>
            <h1 className="font-bold text-lg text-gray-900 dark:text-white">{t("app_name")}</h1>
            <p className="text-xs text-gray-500 dark:text-gray-400">Smart Healthcare</p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-2">
          <NavigationItem icon={Home} label={t("dashboard")} viewId="dashboard" />
          <NavigationItem icon={Bot} label={t("chat")} viewId="chat" />
          <NavigationItem icon={ShoppingCart} label={t("products")} viewId="products" />
          <NavigationItem icon={Package} label={t("orders")} viewId="orders" />
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200 dark:border-gray-700 space-y-3">
          <button
            onClick={() => setIsDarkMode(!isDarkMode)}
            className="w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg
              bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 transition"
          >
            {isDarkMode ? <Sun size={18} /> : <Moon size={18} />}
            <span className="text-sm font-medium">{isDarkMode ? t("light") : t("dark")}</span>
          </button>
          <button
            onClick={onProfileClick}
            className="w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg
              bg-gradient-to-r from-teal-500 to-emerald-500 text-white hover:from-teal-600 hover:to-emerald-600 transition shadow-lg"
          >
            <User size={18} />
            <span className="text-sm font-medium">{t("profile")}</span>
          </button>
        </div>
      </aside>

      {/* Mobile Overlay */}
      {mobileMenuOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-30 md:hidden"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      {/* MAIN CONTENT AREA - Positioned right of fixed sidebar on desktop */}
      <main className="flex-1 flex flex-col overflow-hidden md:ml-64">
        {/* TOP HEADER - FIXED */}
        <div className="flex-shrink-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4 flex items-center justify-between">
          <button
            onClick={() => setMobileMenuOpen(true)}
            className="md:hidden p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
          >
            <MenuIcon size={24} />
          </button>
          <h1 className="font-bold text-lg text-gray-900 dark:text-white">{t("app_name")}</h1>
          <div className="w-8 md:hidden" /> {/* Spacer for alignment (mobile only) */}
        </div>

        {/* SCROLLABLE CONTENT AREA */}
        <div className="flex-1 overflow-y-auto">
          {children}
        </div>
      </main>
    </div>
  );
}

// ==========================================
// MAIN APP COMPONENT
// ==========================================
export default function App() {
  const [role, setRole] = useState(null);
  const [user, setUser] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [view, setView] = useState("dashboard");
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [preferredLanguage, setPreferredLanguage] = useState("en");

  const t = getI18n(preferredLanguage);

  // ==========================================
  // LOGIN FORM
  // ==========================================
  function LoginForm({ onLogin }) {
    const [loginRole, setLoginRole] = useState("user");
    const [loginStep, setLoginStep] = useState("role");
    const [showRegister, setShowRegister] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [loginData, setLoginData] = useState({
      phone: "",
      password: "",
      age: "",
      name: "",
      shopId: "",
    });

    const isAdmin = loginRole === "admin";

    const handleSubmit = async () => {
      setError("");
      
      if (!loginData.password.trim()) {
        setError(t("password_required"));
        return;
      }

      if (showRegister) {
        if (!loginData.name.trim()) {
          setError(t("name_required"));
          return;
        }
        if (isAdmin && !loginData.shopId.trim()) {
          setError(t("shop_id_required"));
          return;
        }
        if (!isAdmin && !loginData.phone.trim()) {
          setError(t("phone_required"));
          return;
        }

        setLoading(true);
        try {
          const res = await axios.post(`${API_BASE}/auth/register`, {
            name: loginData.name,
            phone: isAdmin ? null : loginData.phone,
            shop_id: isAdmin ? loginData.shopId : null,
            password: loginData.password,
            age: isAdmin ? null : (loginData.age ? parseInt(loginData.age) : null),
          });

          if (res.data.success) {
            onLogin(loginRole, res.data.user, res.data.session_id);
          } else {
            setError(res.data.message || "Registration failed");
          }
        } catch (err) {
          setError(err.response?.data?.detail || "Registration error: " + err.message);
        } finally {
          setLoading(false);
        }
      } else {
        if (isAdmin && !loginData.shopId.trim()) {
          setError(t("shop_id_required"));
          return;
        }
        if (!isAdmin && !loginData.phone.trim()) {
          setError(t("phone_required"));
          return;
        }

        setLoading(true);
        try {
          const res = await axios.post(`${API_BASE}/auth/login`, {
            phone: isAdmin ? null : loginData.phone,
            shop_id: isAdmin ? loginData.shopId : null,
            password: loginData.password,
          });

          if (res.data.success) {
            onLogin(loginRole, res.data.user, res.data.session_id);
          } else {
            setError(res.data.message || "Login failed");
          }
        } catch (err) {
          setError(err.response?.data?.detail || "Login error: " + err.message);
        } finally {
          setLoading(false);
        }
      }
    };

    if (loginStep === "role") {
      return (
        <div className="flex items-center justify-center h-screen bg-gradient-to-br from-teal-50 to-emerald-50 dark:from-gray-900 dark:to-gray-800">
          <div className="bg-white dark:bg-gray-800 p-10 rounded-2xl shadow-xl w-full max-w-md">
            <div className="flex items-center justify-center mb-6">
              <div className="w-12 h-12 bg-gradient-to-br from-teal-500 to-emerald-500 rounded-lg flex items-center justify-center">
                <Pill className="text-white" size={28} />
              </div>
            </div>
            <h1 className="text-3xl font-bold text-center mb-2 text-gray-900 dark:text-white">{t("app_name")}</h1>
            <p className="text-center text-gray-600 dark:text-gray-400 mb-6">{t("choose_role")}</p>
            <div className="flex flex-col gap-4">
              <select
                value={loginRole}
                onChange={(e) => setLoginRole(e.target.value)}
                className="border border-gray-300 dark:border-gray-600 p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="user">{t("user_chatbot")}</option>
                <option value="admin">{t("admin_inventory")}</option>
              </select>
              <button
                onClick={() => setLoginStep("credentials")}
                className="w-full px-6 py-3 bg-gradient-to-r from-teal-500 to-emerald-500 text-white rounded-lg hover:from-teal-600 hover:to-emerald-600 transition font-medium"
              >
                {t("continue")}
              </button>
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className="flex items-center justify-center h-screen bg-gradient-to-br from-teal-50 to-emerald-50 dark:from-gray-900 dark:to-gray-800">
        <div className="bg-white dark:bg-gray-800 p-10 rounded-2xl shadow-xl w-full max-w-md">
          <h1 className="text-3xl font-bold text-center mb-6 text-gray-900 dark:text-white">
            {showRegister
              ? t("register_as", { role: isAdmin ? t("admin_inventory") : t("user_chatbot") })
              : t("login_as", { role: isAdmin ? t("admin_inventory") : t("user_chatbot") })}
          </h1>
          
          {error && (
            <div className="mb-4 p-3 bg-red-100 dark:bg-red-900 border border-red-300 dark:border-red-700 text-red-700 dark:text-red-200 rounded-lg text-sm">
              {error}
            </div>
          )}

          <div className="flex flex-col gap-4">
            {!isAdmin && (
              <>
                {showRegister && (
                  <input
                    type="text"
                    placeholder={t("name")}
                    value={loginData.name}
                    onChange={(e) => setLoginData({ ...loginData, name: e.target.value })}
                    className="border border-gray-300 dark:border-gray-600 p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  />
                )}
                <input
                  type="text"
                  placeholder={t("phone_number")}
                  value={loginData.phone}
                  onChange={(e) => setLoginData({ ...loginData, phone: e.target.value })}
                  className="border border-gray-300 dark:border-gray-600 p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
                {showRegister && (
                  <input
                    type="number"
                    placeholder={t("age")}
                    value={loginData.age}
                    onChange={(e) => setLoginData({ ...loginData, age: e.target.value })}
                    className="border border-gray-300 dark:border-gray-600 p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  />
                )}
              </>
            )}

            {isAdmin && (
              <>
                {showRegister && (
                  <input
                    type="text"
                    placeholder={t("name")}
                    value={loginData.name}
                    onChange={(e) => setLoginData({ ...loginData, name: e.target.value })}
                    className="border border-gray-300 dark:border-gray-600 p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  />
                )}
                <input
                  type="text"
                  placeholder={t("shop_id")}
                  value={loginData.shopId}
                  onChange={(e) => setLoginData({ ...loginData, shopId: e.target.value })}
                  className="border border-gray-300 dark:border-gray-600 p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </>
            )}

            <input
              type="password"
              placeholder={t("password")}
              value={loginData.password}
              onChange={(e) => setLoginData({ ...loginData, password: e.target.value })}
              className="border border-gray-300 dark:border-gray-600 p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />

            <button
              onClick={handleSubmit}
              disabled={loading}
              className="w-full px-6 py-3 bg-gradient-to-r from-teal-500 to-emerald-500 text-white rounded-lg hover:from-teal-600 hover:to-emerald-600 transition font-medium disabled:opacity-50"
            >
              {loading ? t("processing") : (showRegister ? t("register") : t("login"))}
            </button>

            <button
              onClick={() => setShowRegister(!showRegister)}
              className="text-center text-sm text-teal-600 dark:text-teal-400 hover:underline"
            >
              {showRegister ? t("already_have_account") : t("dont_have_account")}
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!role || !user) {
    return <LoginForm onLogin={(r, u, s) => { setRole(r); setUser(u); setSessionId(s); }} />;
  }

  // ==========================================
  // DASHBOARD VIEW
  // ==========================================
  const DashboardView = () => (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">{t("welcome_back", { name: user?.name })}</h1>
      <p className="text-gray-500 dark:text-gray-400 mb-8">Your personal pharmacy dashboard</p>
      
      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700">
          <p className="text-gray-600 dark:text-gray-400 text-sm uppercase tracking-wide">Pending Orders</p>
          <p className="text-4xl font-bold text-teal-600 mt-2">5</p>
        </div>
        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700">
          <p className="text-gray-600 dark:text-gray-400 text-sm uppercase tracking-wide">Completed</p>
          <p className="text-4xl font-bold text-emerald-600 mt-2">12</p>
        </div>
        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700">
          <p className="text-gray-600 dark:text-gray-400 text-sm uppercase tracking-wide">Cancelled</p>
          <p className="text-4xl font-bold text-red-600 mt-2">1</p>
        </div>
        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700">
          <p className="text-gray-600 dark:text-gray-400 text-sm uppercase tracking-wide">Nearby Shops</p>
          <p className="text-4xl font-bold text-blue-600 mt-2">2</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Recent Orders</h2>
          <div className="space-y-3">
            <div className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <span className="font-medium text-gray-900 dark:text-white">Paracetamol 500mg</span>
              <span className="px-3 py-1 bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200 rounded-full text-xs font-semibold">Pending</span>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Quick Actions</h2>
          <div className="space-y-3">
            <button onClick={() => setView("chat")} className="w-full px-4 py-3 bg-gradient-to-r from-teal-500 to-emerald-500 text-white rounded-lg hover:from-teal-600 hover:to-emerald-600 transition font-medium">
              Chat with AI
            </button>
            <button onClick={() => setView("products")} className="w-full px-4 py-3 bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition font-medium">
              Browse Products
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  // ==========================================
  // CHAT VIEW (Simplified for brevity)
  // ==========================================
  const ChatView = () => (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">{t("chat_title")}</h1>
      <p className="text-gray-500 dark:text-gray-400 mb-8">{t("chat_subtitle")}</p>
      
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 h-96 flex flex-col overflow-hidden">
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          <div className="flex gap-4">
            <div className="w-8 h-8 rounded-full bg-teal-500 flex items-center justify-center flex-shrink-0">
              <Bot size={16} className="text-white" />
            </div>
            <div className="bg-gray-100 dark:bg-gray-700 p-3 rounded-lg max-w-xs">
              <p className="text-gray-900 dark:text-white text-sm">Hello! How can I help with your health today?</p>
            </div>
          </div>
        </div>

        <div className="border-t border-gray-200 dark:border-gray-700 p-4 flex gap-3">
          <input 
            type="text"
            placeholder={t("input_placeholder")}
            className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          />
          <button className="px-4 py-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600 transition">
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  );

  // ==========================================
  // PRODUCTS VIEW
  // ==========================================
  const ProductsView = () => (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">{t("shop_products")}</h1>
      <p className="text-gray-500 dark:text-gray-400 mb-8">{t("shop_subtitle")}</p>

      <div className="mb-6">
        <input
          type="text"
          placeholder={t("search_products")}
          className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[
          { name: "Paracetamol 500mg", price: "$2.50" },
          { name: "Aspirin 100mg", price: "$3.00" },
          { name: "Vitamin D3", price: "$5.00" },
        ].map((product, idx) => (
          <div key={idx} className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700 hover:shadow-lg transition">
            <h3 className="font-bold text-lg text-gray-900 dark:text-white mb-2">{product.name}</h3>
            <p className="text-teal-600 font-bold text-xl mb-4">{product.price}</p>
            <button className="w-full px-4 py-2 bg-gradient-to-r from-teal-500 to-emerald-500 text-white rounded-lg hover:from-teal-600 hover:to-emerald-600 transition">
              {t("order_now")}
            </button>
          </div>
        ))}
      </div>
    </div>
  );

  // ==========================================
  // ORDERS VIEW
  // ==========================================
  const OrdersView = () => (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Your Orders</h1>
      <p className="text-gray-500 dark:text-gray-400 mb-8">Track all your medicine orders</p>

      <div className="space-y-4">
        {[
          { name: "Paracetamol", qty: 2, status: "Pending", date: "Today" },
          { name: "Cough Syrup", qty: 1, status: "Delivered", date: "2 days ago" },
        ].map((order, idx) => (
          <div key={idx} className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700 flex justify-between items-center">
            <div>
              <h3 className="font-bold text-gray-900 dark:text-white">{order.name}</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">Qty: {order.qty} · {order.date}</p>
            </div>
            <span className={`px-4 py-2 rounded-full text-sm font-semibold
              ${order.status === "Pending" ? "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200" : "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"}`}>
              {order.status}
            </span>
          </div>
        ))}
      </div>
    </div>
  );

  // ==========================================
  // PROFILE MODAL
  // ==========================================
  const ProfileModal = () => (
    <>
      {showProfileModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl max-w-md w-full p-6 shadow-xl">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">{t("profile_title")}</h2>
            
            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{t("name")}</label>
                <input type="text" defaultValue={user?.name} className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{t("language")}</label>
                <select value={preferredLanguage} onChange={(e) => setPreferredLanguage(e.target.value)} className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                  <option value="en">English</option>
                  <option value="hi">हिंदी</option>
                  <option value="mr">मराठी</option>
                </select>
              </div>
            </div>

            <div className="flex gap-3">
              <button onClick={() => setShowProfileModal(false)} className="flex-1 px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition font-medium">
                {t("close")}
              </button>
              <button
                onClick={() => { setRole(null); setUser(null); setSessionId(null); }}
                className="flex-1 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition font-medium"
              >
                {t("logout")}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );

  // ==========================================
  // MAIN LAYOUT WITH NAVIGATION
  // ==========================================
  return (
    <UserLayout
      isDarkMode={isDarkMode}
      setIsDarkMode={setIsDarkMode}
      onProfileClick={() => setShowProfileModal(true)}
      view={view}
      onNavigate={setView}
      currentUser={user}
    >
      {view === "dashboard" && <DashboardView />}
      {view === "chat" && <ChatView />}
      {view === "products" && <ProductsView />}
      {view === "orders" && <OrdersView />}
      
      <ProfileModal />
    </UserLayout>
  );
}
