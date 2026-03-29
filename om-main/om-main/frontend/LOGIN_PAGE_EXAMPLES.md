# Login Page - Implementation Examples & Code Snippets

## Table of Contents
1. [Basic Usage](#basic-usage)
2. [Customization Examples](#customization-examples)
3. [API Integration](#api-integration)
4. [Advanced Features](#advanced-features)
5. [Troubleshooting](#troubleshooting)

---

## Basic Usage

### How LoginPage is Currently Used

In your `App.jsx`:

```javascript
import LoginPage from "./pages/LoginPage";

function App() {
  // ... other state ...
  
  const handleLogin = (role, user, sessionId) => {
    setRole(role);           // Set user role
    setUser(user);           // Store user data
    setSessionId(sessionId); // Store session
    // Component automatically shows dashboard after login
  };

  if (!role) {
    return <LoginPage onLogin={handleLogin} />;
  }

  // Rest of your app...
}
```

---

## Customization Examples

### 1. Change Brand Name & Tagline

**File:** `frontend/src/pages/LoginPage.jsx` (Lines ~145-147)

```javascript
// BEFORE:
<h1 className="login-brand-name">MediPharm</h1>
<p className="login-brand-tagline">Your Trusted Healthcare Partner</p>

// AFTER (Your custom branding):
<h1 className="login-brand-name">MyAppName</h1>
<p className="login-brand-tagline">Your Custom Tagline Here</p>
```

### 2. Change Logo Emoji to Image

**File:** `frontend/src/pages/LoginPage.jsx`

```javascript
// BEFORE:
<div className="login-logo-icon">💊</div>

// AFTER (with image):
<img 
  src="/logo.png" 
  alt="Logo" 
  className="login-logo-image"
  style={{ width: "64px", height: "64px" }}
/>
```

Then add CSS:
```css
.login-logo-image {
  border-radius: 10px;
  animation: bounce 2s ease-in-out infinite;
}
```

### 3. Custom Feature List

**File:** `frontend/src/pages/LoginPage.jsx` (Lines ~173-200)

```javascript
// BEFORE:
<div className="login-features">
  <div className="login-feature-item">
    <div className="login-feature-icon">🔒</div>
    <div>
      <h4>Secure & Private</h4>
      <p>Your data is encrypted and protected</p>
    </div>
  </div>
  {/* ... more features ... */}
</div>

// AFTER (Custom features):
const features = [
  {
    icon: "🚀",
    title: "Lightning Fast",
    description: "Instant results with optimized performance"
  },
  {
    icon: "🌍",
    title: "Global Reach",
    description: "Available in 50+ countries worldwide"
  },
  {
    icon: "💰",
    title: "Affordable Pricing",
    description: "Competitive rates for all budgets"
  }
];

<div className="login-features">
  {features.map((feature, idx) => (
    <div key={idx} className="login-feature-item">
      <div className="login-feature-icon">{feature.icon}</div>
      <div>
        <h4>{feature.title}</h4>
        <p>{feature.description}</p>
      </div>
    </div>
  ))}
</div>
```

### 4. Change Color Scheme

**File:** `frontend/src/styles/LoginPage.css`

```css
/* BEFORE (Purple gradient): */
.login-page {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-submit-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* AFTER (Your brand colors): */
/* Blue theme example */
.login-page {
  background: linear-gradient(135deg, #0066ff 0%, #00ccff 100%);
}

.login-submit-btn {
  background: linear-gradient(135deg, #0066ff 0%, #00ccff 100%);
}

.login-role-btn.active {
  border-color: #0066ff;
  background: linear-gradient(135deg, #0066ff15 0%, #00ccff15 100%);
  color: #0066ff;
  box-shadow: 0 4px 15px rgba(0, 102, 255, 0.2);
}

/* Or use green for healthcare */
.login-page {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.login-submit-btn {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}
```

### 5. Add Social Login Buttons

**File:** `frontend/src/pages/LoginPage.jsx` (After password field)

```javascript
// Add this after the password input in the login form:

{/* Social Login Section */}
<div className="login-divider">
  <span>Or continue with</span>
</div>

<div className="login-social-buttons">
  <button 
    type="button"
    className="login-social-btn"
    onClick={() => {/* Handle Google login */}}
  >
    <svg width="20" height="20" viewBox="0 0 20 20">
      {/* Google icon SVG */}
    </svg>
    Google
  </button>
  
  <button 
    type="button"
    className="login-social-btn"
    onClick={() => {/* Handle Facebook login */}}
  >
    <svg width="20" height="20" viewBox="0 0 20 20">
      {/* Facebook icon SVG */}
    </svg>
    Facebook
  </button>
  
  <button 
    type="button"
    className="login-social-btn"
    onClick={() => {/* Handle Apple login */}}
  >
    <svg width="20" height="20" viewBox="0 0 20 20">
      {/* Apple icon SVG */}
    </svg>
    Apple
  </button>
</div>
```

Add CSS:
```css
.login-divider {
  text-align: center;
  color: #9ca3af;
  position: relative;
  margin: 20px 0;
}

.login-divider::before,
.login-divider::after {
  content: "";
  position: absolute;
  top: 50%;
  width: 40%;
  height: 1px;
  background: #e5e7eb;
}

.login-divider::before {
  left: 0;
}

.login-divider::after {
  right: 0;
}

.login-divider span {
  position: relative;
  background: white;
  padding: 0 10px;
  z-index: 1;
}

.login-social-buttons {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin: 20px 0;
}

.login-social-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px;
  border: 2px solid #e5e7eb;
  background: white;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 12px;
}

.login-social-btn:hover {
  border-color: #667eea;
  background: #f0f4ff;
  transform: translateY(-2px);
}
```

---

## API Integration

### Basic API Response Handling

The LoginPage expects these response formats:

#### Login Success Response:
```javascript
{
  success: true,
  message: "Login successful",
  user: {
    id: "user123",
    name: "John Doe",
    phone: "9876543210",
    email: "john@example.com",
    role: "customer"
  },
  session_id: "session_xyz"
}
```

#### Registration Success Response:
```javascript
{
  success: true,
  message: "Account created successfully",
  user: {
    id: "user456",
    name: "Jane Doe",
    phone: "9876543211",
    shop_id: null
  },
  session_id: "session_abc"
}
```

#### Error Response:
```javascript
{
  success: false,
  message: "Invalid credentials",
  // or
  detail: "Email already exists"
}
```

### Extend API Calls

**File:** `frontend/src/pages/LoginPage.jsx` (Lines ~220-245)

If you need to add extra data to API calls:

```javascript
// BEFORE (existing code):
const response = await axios.post(endpoint, payload);

// AFTER (with extra headers/params):
const response = await axios.post(endpoint, payload, {
  headers: {
    "Authorization": `Bearer ${token}`,
    "X-Custom-Header": "value"
  }
});

// Or with interceptors (in main.jsx):
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem("authToken");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### Handle 2FA (Two-Factor Authentication)

```javascript
// After adding this state in LoginPage:
const [requires2FA, setRequires2FA] = useState(false);
const [otpData, setOtpData] = useState("");

// Modify login handler:
try {
  const response = await axios.post(endpoint, payload);
  
  if (response.data.requires_2fa) {
    setRequires2FA(true);
    localStorage.setItem("tempSessionId", response.data.temp_session_id);
  } else if (response.data.success) {
    // Normal login flow
  }
} catch (err) {
  // Error handling
}

// Add OTP input field:
{requires2FA && (
  <div className="login-form-group">
    <label className="login-label">Enter 6-digit Code</label>
    <input
      type="text"
      value={otpData}
      onChange={(e) => setOtpData(e.target.value)}
      placeholder="000000"
      maxLength="6"
      pattern="\d{6}"
      className="login-input"
    />
  </div>
)}
```

---

## Advanced Features

### 1. Remember Me with Auto-Login

```javascript
// Add to App.jsx:
useEffect(() => {
  const savedEmail = localStorage.getItem("rememberedEmail");
  const savedRole = localStorage.getItem("savedRole");
  
  if (savedEmail && savedRole) {
    // Show pre-filled form
    setFormData(prev => ({
      ...prev,
      email: savedEmail
    }));
    setUserRole(savedRole);
  }
}, []);

// In LoginForm:
if (rememberMe && response.data.success) {
  localStorage.setItem("rememberedEmail", formData.email);
  localStorage.setItem("savedRole", userRole);
  // Auto-login: call onLogin immediately
}
```

### 2. Password Strength Indicator

Add to LoginPage.jsx:

```javascript
const getPasswordStrength = (password) => {
  let strength = 0;
  
  if (password.length >= 8) strength++;
  if (password.length >= 12) strength++;
  if (/[A-Z]/.test(password)) strength++;
  if (/[a-z]/.test(password)) strength++;
  if (/\d/.test(password)) strength++;
  if (/[^A-Za-z0-9]/.test(password)) strength++;
  
  return strength <= 2 ? "weak" : strength <= 4 ? "medium" : "strong";
};

// Add to form:
{activeTab === "register" && (
  <>
    <div className="login-password-strength">
      <div className={`strength-bar strength-${getPasswordStrength(formData.password)}`} />
      <span className="strength-text">{getPasswordStrength(formData.password)}</span>
    </div>
  </>
)}
```

CSS for password strength:
```css
.login-password-strength {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: -10px;
}

.strength-bar {
  height: 4px;
  width: 100%;
  border-radius: 2px;
  background: #e5e7eb;
}

.strength-weak { background: #ef4444; }
.strength-medium { background: #f59e0b; }
.strength-strong { background: #10b981; }

.strength-text {
  font-size: 12px;
  color: #6b7280;
}
```

### 3. Email Verification Flow

```javascript
const [verificationStep, setVerificationStep] = useState(null);
const [verificationCode, setVerificationCode] = useState("");

// After registration:
if (response.data.requires_email_verification) {
  setVerificationStep("email");
  setSuccess("Verification link sent to your email");
}

// Add verification UI:
{verificationStep === "email" && (
  <>
    <p>Check your email for verification link</p>
    <input
      type="text"
      value={verificationCode}
      onChange={(e) => setVerificationCode(e.target.value)}
      placeholder="Paste verification code"
      className="login-input"
    />
    <button onClick={handleEmailVerification}>
      Verify Email
    </button>
  </>
)}
```

### 4. Multi-Step Registration

```javascript
const [registrationStep, setRegistrationStep] = useState(1);

// Step 1: Basic Info
// Step 2: Password
// Step 3: Verification

{registrationStep === 1 && (
  <div>
    {/* Name & email fields */}
    <button onClick={() => setRegistrationStep(2)}>Next</button>
  </div>
)}

{registrationStep === 2 && (
  <div>
    {/* Password fields */}
    <button onClick={() => setRegistrationStep(3)}>Next</button>
    <button onClick={() => setRegistrationStep(1)}>Back</button>
  </div>
)}

{registrationStep === 3 && (
  <div>
    {/* Review & submit */}
    <button onClick={handleRegistration}>Complete</button>
  </div>
)}
```

---

## Troubleshooting

### Issue: Styles not loading

```javascript
// Check import in LoginPage.jsx:
import "../styles/LoginPage.css"; // ✅ Correct
import "styles/LoginPage.css";    // ❌ Wrong

// Verify file exists at:
frontend/src/styles/LoginPage.css
```

### Issue: Login endpoint not found

```javascript
// Verify API_BASE is correct:
const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";
                                 ↑ Must be defined in .env file

// Create .env file in frontend/:
VITE_API_BASE_URL=http://localhost:8000
VITE_SOCKET_URL=http://localhost:8000
```

### Issue: CORS errors

```javascript
// Backend (Flask/FastAPI example):
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "your-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: Form not submitting

```javascript
// Check browser console (F12) for:
1. Network errors (CORS, 404, 500)
2. JavaScript errors
3. API response format

// Log for debugging:
console.log("Form data:", formData);
console.log("Response:", response.data);
console.log("Error:", error);
```

---

## Testing Examples

### Unit Test (Jest)
```javascript
import { render, screen, fireEvent } from "@testing-library/react";
import LoginPage from "./LoginPage";

describe("LoginPage", () => {
  it("renders login form", () => {
    render(<LoginPage onLogin={jest.fn()} />);
    expect(screen.getByText("Sign In")).toBeInTheDocument();
  });

  it("shows error for invalid email", () => {
    const { getByPlaceholderText } = render(
      <LoginPage onLogin={jest.fn()} />
    );
    fireEvent.change(getByPlaceholderText("Email"), {
      target: { value: "invalid" }
    });
    fireEvent.click(screen.getByText("Sign In"));
    expect(screen.getByText(/invalid email/i)).toBeInTheDocument();
  });
});
```

### Manual Testing Checklist
```
Desktop:
☐ Load page, see 2-column layout
☐ Test all 3 roles
☐ Submit login, see spinner
☐ Switch to register tab

Mobile:
☐ Single column layout
☐ Touch-friendly buttons
☐ Form scrolls properly
☐ All text readable

Form:
☐ Validation errors appear
☐ Password toggle works
☐ Remember me checkbox
☐ Success messages show

API:
☐ Login successful
☐ Registration works
☐ Error messages display
☐ Session ID returned
```

---

**Now you have all the examples and code snippets needed to customize your login page!** ✨
