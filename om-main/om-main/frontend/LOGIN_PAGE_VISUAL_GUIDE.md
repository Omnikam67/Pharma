# Login Page - Visual Layout Guide

## Overall Layout Structure

```
┌─────────────────────────────────────────────────────────────────────┐
│                          LOGIN PAGE                                 │
│  ════════════════════════════════════════════════════════════════   │
│                                                                     │
│  ╔════════════════════════════╦════════════════════════════════╗  │
│  ║                            ║                                ║  │
│  ║   LEFT PANEL               ║   RIGHT PANEL                  ║  │
│  ║   (Branding)               ║   (Login Form)                 ║  │
│  ║                            ║                                ║  │
│  ║  ┌──────────────────┐     ║  ┌──────────────────────────┐ ║  │
│  ║  │      LOGO        │     ║  │  ROLE SELECTOR           │ ║  │
│  ║  │  💊 MediPharm    │     ║  │  [👤] [💊] [🩺]         │ ║  │
│  ║  │  Trusted Partner │     ║  │  Customer Pharmacist..   │ ║  │
│  ║  └──────────────────┘     ║  └──────────────────────────┘ ║  │
│  ║                            ║                                ║  │
│  ║  FEATURES:                ║  ┌──────────────────────────┐ ║  │
│  ║  ━━━━━━━━━━━━━━━━━━━━━━ ║  │  TAB SELECTOR            │ ║  │
│  ║  🔒 Secure & Private     ║  │  [Sign In] [Sign Up]     │ ║  │
│  ║  ⚡ Fast & Reliable      ║  └──────────────────────────┘ ║  │
│  ║  🏥 Professional Care     ║                                ║  │
│  ║                            ║  ┌──────────────────────────┐ ║  │
│  ║                            ║  │  FORM FIELDS             │ ║  │
│  ║                            ║  │  ┌──────────────────┐   │ ║  │
│  ║                            ║  │  │ 📧 Email/Phone   │   │ ║  │
│  ║                            ║  │  └──────────────────┘   │ ║  │
│  ║                            ║  │  ┌──────────────────┐   │ ║  │
│  ║                            ║  │  │ 🔐 Password      │   │ ║  │
│  ║                            ║  │  └──────────────────┘   │ ║  │
│  ║                            ║  │  ☑️ Remember me         │ ║  │
│  ║                            ║  └──────────────────────────┘ ║  │
│  ║                            ║                                ║  │
│  ║                            ║  ┌──────────────────────────┐ ║  │
│  ║                            ║  │   [ SIGN IN BUTTON ]     │ ║  │
│  ║                            ║  └──────────────────────────┘ ║  │
│  ║                            ║                                ║  │
│  ╚════════════════════════════╩════════════════════════════════╝  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Desktop View (> 1024px)

```
┌────────────────────────────────────────────────────────────────────┐
│                                                                    │
│  ╔─────────────────────────┬──────────────────────────────────╗  │
│  │                         │                                  │  │
│  │   BRANDING PANEL        │     LOGIN FORM SECTION          │  │
│  │   ━━━━━━━━━━━━━━━━━━    │     ━━━━━━━━━━━━━━━━━━         │  │
│  │                         │                                  │  │
│  │   💊 MediPharm          │   👤 💊 🩺                      │  │
│  │   Trusted Healthcare    │   ┌─────────────────┐          │  │
│  │   Partner               │   │ Customer/...    │          │  │
│  │                         │   └─────────────────┘          │  │
│  │                         │                                  │  │
│  │   Features:             │   [Sign In] [Sign Up]           │  │
│  │   🔒 Secure              │                                  │  │
│  │   ⚡ Fast                │   Error/Success Messages        │  │
│  │   🏥 Professional        │                                  │  │
│  │                         │   Email/Phone Input              │  │
│  │                         │   Password Input                 │  │
│  │                         │   Password Input (confirm)       │  │
│  │                         │   Age/Shop ID (if needed)        │  │
│  │                         │                                  │  │
│  │                         │   ☑️ Remember me                 │  │
│  │                         │   ? Forgot password              │  │
│  │                         │                                  │  │
│  │                         │   ┌──────────────────┐           │  │
│  │                         │   │ Sign In Button   │           │  │
│  │                         │   └──────────────────┘           │  │
│  │                         │                                  │  │
│  │                         │   Terms & Privacy Links          │  │
│  │                         │                                  │  │
│  ╚─────────────────────────┴──────────────────────────────────╝  │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

## Tablet View (768px - 1024px)

```
┌──────────────────────────────────┐
│      (Branding Hidden)           │
│                                  │
│  ┌──────────────────────────┐   │
│  │ 👤 💊 🩺                │   │
│  │ Role Selection           │   │
│  └──────────────────────────┘   │
│                                  │
│  ┌──────────────────────────┐   │
│  │ [Sign In] [Sign Up]      │   │
│  └──────────────────────────┘   │
│                                  │
│  Form Content                    │
│  ┌──────────────────────────┐   │
│  │ Email/Phone Input        │   │
│  │ Password Input           │   │
│  │ Additional Fields        │   │
│  │                          │   │
│  │ [Sign In Button]         │   │
│  └──────────────────────────┘   │
│                                  │
└──────────────────────────────────┘
```

## Mobile View (< 480px)

```
┌──────────────┐
│Full screen   │
│              │
│ 👤 💊 🩺    │
│ Roles        │
│              │
│[Sign In]     │
│[Sign Up]     │
│              │
│Email/Phone   │
│──────────────│
│              │
│Password      │
│──────────────│
│              │
│[Sign In]     │
│              │
│Terms & Links │
│              │
└──────────────┘
```

## Role Selector States

```
INACTIVE STATE:
┌──────────────────────────────────────┐
│  👤            💊            🩺       │
│ Customer      Pharmacist     Doctor   │
│ (light bg)   (light bg)    (light bg) │
└──────────────────────────────────────┘

ACTIVE STATE (Customer selected):
┌──────────────────────────────────────┐
│  👤            💊            🩺       │
│ Customer      Pharmacist     Doctor   │
│(dark bg)     (light bg)    (light bg) │
│(blue color)                           │
│(blue shadow)                          │
└──────────────────────────────────────┘
```

## Form Input States

```
NORMAL STATE:
┌─────────────────────────┐
│ 📧 example@email.com    │
└─────────────────────────┘

FOCUSED STATE:
┌─────────────────────────┐
│ 📧 example@email.com    │ ← Blue border
└─────────────────────────┘ ← Blue glow

FILLED STATE:
✓ test@example.com

ERROR STATE:
⚠️ Invalid email format
┌─────────────────────────┐
│ Email address required  │  ← Red border
└─────────────────────────┘    ← Red background

DISABLED STATE:
┌─────────────────────────┐
│ 📧                      │   ← Grayed out
└─────────────────────────┘    ← Low opacity
```

## Password Input with Toggle

```
NORMAL (hidden):
┌─────────────────────────────────┐
│ 🔐 ••••••••••••••••••  👁️       │
│    (password hidden)    (eye icon)
└─────────────────────────────────┘

VISIBLE (clicked):
┌─────────────────────────────────┐
│ 🔐 mySecurePassword123  👁️‍🗨️    │
│    (text visible)     (different icon)
└─────────────────────────────────┘
```

## Alert Messages

```
ERROR ALERT:
┌─────────────────────────────────┐
│ ⚠️ Invalid phone number        │
│    (red text on pink background)│
└─────────────────────────────────┘

SUCCESS ALERT:
┌─────────────────────────────────┐
│ ✓ Login successful!            │
│   (green text on light green bg) │
└─────────────────────────────────┘
```

## Button States

```
NORMAL STATE:
┌──────────────────────┐
│  Sign In             │
│ (purple gradient)    │
└──────────────────────┘

HOVER STATE:
┌──────────────────────┐
│  Sign In             │
│ (darker purple)      │
│ (shadow effect)      │
│ (move up slightly)   │
└──────────────────────┘

ACTIVE STATE:
┌──────────────────────┐
│  Sign In             │
│ (pressed effect)     │
│ (no shadow)          │
└──────────────────────┘

LOADING STATE:
┌──────────────────────┐
│  ⟳ Signing In...     │
│ (spinner icon)       │
│ (disabled)           │
│ (opacity reduced)    │
└──────────────────────┘

DISABLED STATE:
┌──────────────────────┐
│  Sign In             │
│ (gray background)    │
│ (no interaction)     │
└──────────────────────┘
```

## Color States

```
TEXT STATUS:
✓ Valid input        → Green text
✗ Invalid input      → Red text
⊘ Disabled field     → Gray text
→ Focused field      → Blue text
◉ Active role/tab    → Blue/Purple

BACKGROUND STATUS:
Normal input         → #fafbfc (light blue-gray)
Focused input        → #ffffff (white)
Disabled input       → #f3f4f6 (light gray)
Error input          → #fee (light red)
Success message      → #efe (light green)
Error message        → #fee (light red)
```

## Animation Flows

```
PAGE LOAD ANIMATION:
0ms: Opacity 0, Y position +40px
↓
400ms: Slide up smoothly
↓
800ms: Full opacity, Y position 0

BUTTON HOVER:
Normal state
↓ (300ms)
Translate Y: -2px
↓
Shadow: Higher opacity
↓
Leave hover
↓ (300ms)
Back to normal

SPINNER ANIMATION:
┌─────┐
│ ⟳   │ Rotates 360°
└─────┘   every 0.8 seconds
   ↻
```

## Responsive Breakpoints Guide

```
MOBILE (< 480px)
└─ Full width form
   Full height viewport
   Touch-optimized
   Compact spacing

TABLET (480px - 768px)
└─ Wider form
   Centered layout
   Medium spacing

DESKTOP (768px - 1024px)
└─ Single column (no branding)
   Larger form
   Generous spacing

LARGE DESKTOP (> 1024px)
└─ Two column layout
   Branding visible
   Maximum spacing
   Full decorations visible
```

## Z-Index Hierarchy

```
100 ─── Spinner (modal-like)
 90 ─── Alerts/Messages
 80 ─── Form Container
 70 ─── Input Focus Glow
 60 ─── Buttons
 50 ─── Icons
 40 ─── Text
 30 ─── Background
 20 ─── Decorative Shapes
 10 ─── Main Background
```

## Component Spacing Guide

```
Container Padding:     40px (desktop), 20px (mobile)
Element Gap:          20px (form groups), 12px (buttons)
Label to Input:       8px
Icon to Text:         12px
Button Height:        14px padding top/bottom
Border Radius:        10px (inputs), 12px (containers)
Animation Duration:   0.3s (transitions), 0.8s (keyframes)
Shadow Blur:          20-60px depending on element
```

---

**Visual Design System Complete & Consistent**
✅ All states covered
✅ All screen sizes optimized
✅ All interactions smooth
✅ Professional appearance maintained
