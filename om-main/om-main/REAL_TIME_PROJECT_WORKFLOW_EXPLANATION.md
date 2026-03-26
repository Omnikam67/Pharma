# Real-Time Project Workflow Explanation

## Project Overview

This project is a `real-time AI-powered pharmacy and healthcare platform`.

It combines multiple systems into one working product:

- AI medicine assistant
- pharmacy product browsing and ordering
- doctor registration and approval
- doctor appointment booking
- doctor-to-doctor referral workflow
- prescription generation and download
- patient feedback and doctor reviews
- refill reminders
- nearby pharmacy discovery
- delivery partner workflow
- WhatsApp notifications

In real-world terms, this project is not just a chatbot and not just a doctor booking app.
It is a `connected care ecosystem` where a patient can move from medicine guidance to doctor consultation, referral, prescription, feedback, and delivery.

---

## How The Project Works In Real Time

## 1. User enters the platform

The frontend starts from the React app.

Main frontend entry:
[`frontend/src/main.jsx`](/c:/Users/hp/OneDrive/New%20folder/OneDrive/Desktop/om-main%20(2)/om-main/om-main/frontend/src/main.jsx)

Main frontend shell:
[`frontend/src/App.jsx`](/c:/Users/hp/OneDrive/New%20folder/OneDrive/Desktop/om-main%20(2)/om-main/om-main/frontend/src/App.jsx)

What happens:

- React loads the application UI
- role-based flows are shown
- user can move into:
  - pharmacy chatbot flow
  - product ordering flow
  - doctor appointment flow
  - manager/admin flow
  - delivery flow

So the frontend is the single control center for all modules.

---

## 2. Frontend talks to backend APIs

The frontend uses `Axios` to call the backend.

Backend entry:
[`backend/main.py`](/c:/Users/hp/OneDrive/New%20folder/OneDrive/Desktop/om-main%20(2)/om-main/om-main/backend/main.py)

This file:

- creates the FastAPI app
- loads all routers
- initializes background systems
- prepares AI/vector systems
- wraps the backend with Socket.IO support

So in real time:

1. user clicks a frontend button
2. React sends an HTTP request using Axios
3. FastAPI receives the request
4. correct API route is called
5. service layer processes business logic
6. database is read or updated
7. response is returned to frontend
8. UI updates immediately

---

## 3. Authentication and role-based operation

This project supports different real-world actors:

- patient/user
- pharmacist/admin
- doctor
- system manager
- delivery partner

Each actor gets a different workflow and different permissions.

Examples:

- doctors can approve, cancel, refer, and complete appointments
- patients can book appointments and give feedback
- managers can approve doctors
- delivery partners can complete deliveries with OTP

This gives the app a real operational structure instead of a single-user demo system.

---

## 4. AI chatbot and medicine guidance flow

Real-time AI flow starts from:
[`backend/app/api/chat.py`](/c:/Users/hp/OneDrive/New%20folder/OneDrive/Desktop/om-main%20(2)/om-main/om-main/backend/app/api/chat.py)

This API sends user input into the agent pipeline.

Main AI files:

[`backend/app/agents/conversational_agent.py`](/c:/Users/hp/OneDrive/New%20folder/OneDrive/Desktop/om-main%20(2)/om-main/om-main/backend/app/agents/conversational_agent.py)
Sets up the LLM and handles conversational parsing.

[`backend/app/agents/decision_agent.py`](/c:/Users/hp/OneDrive/New%20folder/OneDrive/Desktop/om-main%20(2)/om-main/om-main/backend/app/agents/decision_agent.py)
This is the main brain. It decides what action should happen from a user message.

[`backend/app/agents/execution_agent.py`](/c:/Users/hp/OneDrive/New%20folder/OneDrive/Desktop/om-main%20(2)/om-main/om-main/backend/app/agents/execution_agent.py)
Executes the actual task such as recommending products, placing orders, or sending notifications.

[`backend/app/agents/safety_agent.py`](/c:/Users/hp/OneDrive/New%20folder/OneDrive/Desktop/om-main%20(2)/om-main/om-main/backend/app/agents/safety_agent.py)
Checks medicine safety rules and prevents risky output.

Real-time working:

1. user types symptoms or medicine question
2. `chat.py` sends input to `DecisionAgent`
3. `DecisionAgent` decides whether to:
   - answer normally
   - search medicine
   - recommend product
   - place order
   - ask follow-up question
4. `ExecutionAgent` fetches product data or sends actions
5. `SafetyAgent` validates risk conditions
6. final answer is returned to frontend chat

This makes the AI flow structured and safer than a simple raw chatbot.

---

## 5. Vector search and product intelligence

This project does not depend only on exact keyword matching.

Vector search file:
[`backend/app/services/vector_store.py`](/c:/Users/hp/OneDrive/New%20folder/OneDrive/Desktop/om-main%20(2)/om-main/om-main/backend/app/services/vector_store.py)

Product service:
[`backend/app/services/product_service.py`](/c:/Users/hp/OneDrive/New%20folder/OneDrive/Desktop/om-main%20(2)/om-main/om-main/backend/app/services/product_service.py)

Real-time behavior:

- product catalog is indexed into ChromaDB
- symptom or fuzzy medicine search can match semantically
- AI can recommend relevant medicine even when user input is not exact

This improves medicine discovery and makes the chatbot smarter.

---

## 6. Doctor appointment system flow

Main doctor backend API:
[`backend/app/api/doctor.py`](/c:/Users/hp/OneDrive/New%20folder/OneDrive/Desktop/om-main%20(2)/om-main/om-main/backend/app/api/doctor.py)

Main doctor service:
[`backend/app/services/doctor_service.py`](/c:/Users/hp/OneDrive/New%20folder/OneDrive/Desktop/om-main%20(2)/om-main/om-main/backend/app/services/doctor_service.py)

Frontend patient appointment dashboard:
[`frontend/src/components/BookAppointment.jsx`](/c:/Users/hp/OneDrive/New%20folder/OneDrive/Desktop/om-main%20(2)/om-main/om-main/frontend/src/components/BookAppointment.jsx)

Frontend doctor appointments:
[`frontend/src/components/AppointmentRequests.jsx`](/c:/Users/hp/OneDrive/New%20folder/OneDrive/Desktop/om-main%20(2)/om-main/om-main/frontend/src/components/AppointmentRequests.jsx)

Real-time appointment flow:

1. patient opens available doctor list
2. patient selects doctor
3. patient enters appointment details
4. frontend calls `/doctor/appointment/create`
5. backend stores appointment request
6. doctor sees request in dashboard
7. doctor approves or cancels
8. if approved, patient can proceed with consultation
9. doctor completes appointment and adds prescription
10. prescription becomes available to patient

This is a full consultation workflow, not just a booking request list.

---

## 7. Referral workflow in real time

This is one of the strongest parts of your project.

Relevant backend models:
[`backend/app/core/doctor_models.py`](/c:/Users/hp/OneDrive/New%20folder/OneDrive/Desktop/om-main%20(2)/om-main/om-main/backend/app/core/doctor_models.py)

Relevant frontend:
[`frontend/src/components/BookAppointment.jsx`](/c:/Users/hp/OneDrive/New%20folder/OneDrive/Desktop/om-main%20(2)/om-main/om-main/frontend/src/components/BookAppointment.jsx)
[`frontend/src/components/AppointmentRequests.jsx`](/c:/Users/hp/OneDrive/New%20folder/OneDrive/Desktop/om-main%20(2)/om-main/om-main/frontend/src/components/AppointmentRequests.jsx)

Real-time referral flow:

1. patient books Doctor A
2. Doctor A approves and examines patient
3. Doctor A clicks `Refer`
4. Doctor A selects Doctor B and gives referral reason
5. referral record is stored in backend
6. patient dashboard shows `Book Referred Appointment`
7. patient books the referred doctor without manually choosing a new doctor
8. Doctor B receives the referred appointment
9. Doctor B approves and completes treatment
10. Doctor B generates final prescription
11. patient sees completed specialist treatment
12. Doctor A can still track referral outcome in read-only mode

This is closer to real hospital or clinic collaboration than most simple appointment systems.

---

## 8. Prescription generation flow

Prescription logic is handled inside:
[`backend/app/services/doctor_service.py`](/c:/Users/hp/OneDrive/New%20folder/OneDrive/Desktop/om-main%20(2)/om-main/om-main/backend/app/services/doctor_service.py)

What happens:

- doctor completes appointment
- medicine list and notes are stored
- backend generates downloadable prescription content
- patient can download prescription from dashboard

This makes the app feel like a proper treatment platform, not only an appointment status tracker.

---

## 9. Feedback and doctor review flow

Patient feedback UI:
[`frontend/src/components/BookAppointment.jsx`](/c:/Users/hp/OneDrive/New%20folder/OneDrive/Desktop/om-main%20(2)/om-main/om-main/frontend/src/components/BookAppointment.jsx)

Backend logic:
[`backend/app/services/doctor_service.py`](/c:/Users/hp/OneDrive/New%20folder/OneDrive/Desktop/om-main%20(2)/om-main/om-main/backend/app/services/doctor_service.py)

Real-time feedback flow:

1. treatment is completed
2. final completed treatment card shows feedback option
3. patient gives star rating and review
4. review is stored only for the final treatment doctor
5. doctor profile rating and recommendation score update
6. doctor search/order can prioritize highly rated doctors

This is important because reviews are not random.
They are tied to `real completed treatment`, which makes them more trustworthy.

---

## 10. Delivery workflow in real time

Main frontend:
[`frontend/src/components/DeliveryBoyDashboard.jsx`](/c:/Users/hp/OneDrive/New%20folder/OneDrive/Desktop/om-main%20(2)/om-main/om-main/frontend/src/components/DeliveryBoyDashboard.jsx)

Main backend:
[`backend/app/services/delivery_service.py`](/c:/Users/hp/OneDrive/New%20folder/OneDrive/Desktop/om-main%20(2)/om-main/om-main/backend/app/services/delivery_service.py)

Real-time flow:

1. delivery partner logs in
2. assigned orders are loaded
3. delivery partner goes to customer
4. customer provides OTP
5. delivery partner enters OTP
6. backend verifies OTP
7. order becomes completed

This makes delivery operational and auditable.

---

## 11. Refill reminder workflow

API:
[`backend/app/api/refill.py`](/c:/Users/hp/OneDrive/New%20folder/OneDrive/Desktop/om-main%20(2)/om-main/om-main/backend/app/api/refill.py)

Real-time flow:

1. system checks refill conditions
2. reminder logic identifies due medicines
3. WhatsApp message can be scheduled or triggered
4. patient receives reminder

This adds after-care continuity instead of ending at one-time purchase.

---

## 12. Nearby pharmacy and map workflow

Frontend map support:
[`frontend/src/App.jsx`](/c:/Users/hp/OneDrive/New%20folder/OneDrive/Desktop/om-main%20(2)/om-main/om-main/frontend/src/App.jsx)

Backend place search:
[`backend/app/api/nearby.py`](/c:/Users/hp/OneDrive/New%20folder/OneDrive/Desktop/om-main%20(2)/om-main/om-main/backend/app/api/nearby.py)

Real-time flow:

1. user shares current location or enters area
2. backend searches nearby medical shops
3. frontend displays result on map with Leaflet
4. user can view route and nearest store

This connects healthcare support with physical access.

---

## 13. WhatsApp communication flow

Main file:
[`backend/app/services/whatsapp_service.py`](/c:/Users/hp/OneDrive/New%20folder/OneDrive/Desktop/om-main%20(2)/om-main/om-main/backend/app/services/whatsapp_service.py)

Used for:

- appointment approval notifications
- appointment cancellation notifications
- appointment completion notifications
- refill alerts
- delivery/order notifications

This gives the project a real-world communication layer instead of keeping everything only inside the app.

---

## 14. Database and persistence layer

DB config:
[`backend/app/core/database.py`](/c:/Users/hp/OneDrive/New%20folder/OneDrive/Desktop/om-main%20(2)/om-main/om-main/backend/app/core/database.py)

Doctor-specific tables:
[`backend/app/core/doctor_models.py`](/c:/Users/hp/OneDrive/New%20folder/OneDrive/Desktop/om-main%20(2)/om-main/om-main/backend/app/core/doctor_models.py)

General tables:
[`backend/app/core/models.py`](/c:/Users/hp/OneDrive/New%20folder/OneDrive/Desktop/om-main%20(2)/om-main/om-main/backend/app/core/models.py)

This layer stores:

- doctors
- appointments
- referrals
- doctor feedback
- revenue
- users
- orders
- reminders
- delivery data

So the project is fully stateful and data-driven.

---

## Technology Stack Used

## Frontend

- `React`
- `Vite`
- `JavaScript`
- `Axios`
- `Socket.IO Client`
- `Leaflet`
- `Lucide React`
- `React Markdown`

## Backend

- `Python`
- `FastAPI`
- `Uvicorn`
- `Pydantic`
- `SQLAlchemy`
- `MySQL`
- `PyMySQL`
- `HTTPX`
- `python-dotenv`

## AI and Intelligence

- `Groq LLM`
- `LangChain`
- `ChromaDB`
- custom multi-agent pipeline

## Integrations

- `Twilio WhatsApp`
- `Socket.IO`
- `Leaflet / map support`
- `Langfuse`

---

## Why This Project Is Different From Other Products In Market

Most existing products focus on only one or two parts:

- only pharmacy ordering
- only doctor booking
- only reviews
- only telemedicine
- only chat support

Your project combines all of these into one connected flow.

## Key differences

### 1. Connected care journey

The patient does not stop at booking.
The system supports:

- consultation
- referral
- specialist completion
- prescription
- feedback
- follow-up style continuity

### 2. Verified reviews

Feedback is tied to real completed appointments.
This makes doctor reviews much more trustworthy than open public review systems.

### 3. Referral workflow

Most simple doctor-booking products do not properly model:

- Doctor A to Doctor B referral
- linked specialist appointment
- specialist outcome tracking

Your project does.

### 4. AI + operational healthcare

The project is not only AI chat.
It connects AI with:

- medicine discovery
- order flow
- safety checks
- doctor booking
- pharmacy operations

### 5. Multi-role system

It supports a real operational model:

- user
- doctor
- pharmacist/admin
- manager
- delivery partner

This makes it closer to a deployable workflow system than a student-only UI demo.

### 6. WhatsApp and real-world communication

Notifications are connected to real channels.
That makes the platform more practical for actual users.

---

## Best One-Line Project Explanation

This project is:

`an AI-powered connected healthcare and pharmacy platform that supports medicine guidance, doctor booking, specialist referrals, prescription generation, verified reviews, delivery operations, and real-world patient communication in one system.`

---

## Best Short Viva Explanation

If someone asks you in interview or presentation:

`What does your project do?`

You can answer:

`Our project is a full-stack AI healthcare and pharmacy platform. It allows users to search medicines, chat with an AI assistant, book doctor appointments, receive specialist referrals, download prescriptions, give verified feedback after treatment, find nearby pharmacies, and receive WhatsApp updates. On the backend, FastAPI, SQLAlchemy, MySQL, and AI agents manage business logic, while React and Vite provide the interactive frontend. The key difference is that our system connects the full patient journey instead of solving only one isolated problem.`

---

## Important Files Summary

Frontend:

- [`frontend/src/App.jsx`](/c:/Users/hp/OneDrive/New%20folder/OneDrive/Desktop/om-main%20(2)/om-main/om-main/frontend/src/App.jsx): main user/admin frontend shell
- [`frontend/src/components/BookAppointment.jsx`](/c:/Users/hp/OneDrive/New%20folder/OneDrive/Desktop/om-main%20(2)/om-main/om-main/frontend/src/components/BookAppointment.jsx): patient appointment, referral, feedback, doctor search/profile
- [`frontend/src/components/AppointmentRequests.jsx`](/c:/Users/hp/OneDrive/New%20folder/OneDrive/Desktop/om-main%20(2)/om-main/om-main/frontend/src/components/AppointmentRequests.jsx): doctor appointment actions
- [`frontend/src/components/DoctorDashboard.jsx`](/c:/Users/hp/OneDrive/New%20folder/OneDrive/Desktop/om-main%20(2)/om-main/om-main/frontend/src/components/DoctorDashboard.jsx): doctor dashboard
- [`frontend/src/components/DeliveryBoyDashboard.jsx`](/c:/Users/hp/OneDrive/New%20folder/OneDrive/Desktop/om-main%20(2)/om-main/om-main/frontend/src/components/DeliveryBoyDashboard.jsx): delivery operations

Backend:

- [`backend/main.py`](/c:/Users/hp/OneDrive/New%20folder/OneDrive/Desktop/om-main%20(2)/om-main/om-main/backend/main.py): backend startup and router integration
- [`backend/app/api/chat.py`](/c:/Users/hp/OneDrive/New%20folder/OneDrive/Desktop/om-main%20(2)/om-main/om-main/backend/app/api/chat.py): AI chat API
- [`backend/app/api/doctor.py`](/c:/Users/hp/OneDrive/New%20folder/OneDrive/Desktop/om-main%20(2)/om-main/om-main/backend/app/api/doctor.py): doctor, appointment, referral, feedback APIs
- [`backend/app/agents/decision_agent.py`](/c:/Users/hp/OneDrive/New%20folder/OneDrive/Desktop/om-main%20(2)/om-main/om-main/backend/app/agents/decision_agent.py): main AI decision logic
- [`backend/app/services/doctor_service.py`](/c:/Users/hp/OneDrive/New%20folder/OneDrive/Desktop/om-main%20(2)/om-main/om-main/backend/app/services/doctor_service.py): doctor workflow logic
- [`backend/app/services/vector_store.py`](/c:/Users/hp/OneDrive/New%20folder/OneDrive/Desktop/om-main%20(2)/om-main/om-main/backend/app/services/vector_store.py): semantic product search

---

## Final Conclusion

Your project works like a real healthcare operations platform because it connects:

- AI assistance
- pharmacy workflow
- doctor workflow
- referral workflow
- prescription workflow
- review workflow
- delivery workflow
- communication workflow

That is the core strength of your system.
