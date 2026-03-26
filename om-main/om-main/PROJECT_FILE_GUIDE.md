# Project File Guide

## Overview

This project is an AI-powered pharmacy platform built with:

- `FastAPI` backend
- `React + Vite` frontend
- `MySQL + SQLAlchemy` database
- `Groq + LangChain` for chat understanding
- `ChromaDB` for product retrieval
- `Twilio WhatsApp` for alerts

Main user flows:

- medicine chat and ordering
- symptom-based suggestions
- refill reminders
- medical report analysis
- nearby pharmacy search
- doctor booking and doctor dashboards
- delivery staff workflow
- admin/pharmacist approval and inventory management

## Architecture

1. `frontend/src/App.jsx` and related components handle the UI.
2. The frontend calls FastAPI routes in `backend/app/api/`.
3. Chat requests go through `chat.py`.
4. `conversational_agent.py` parses the message.
5. `decision_agent.py` decides what action to take.
6. `execution_agent.py` performs the action through services.
7. Services talk to MySQL, ChromaDB, and Twilio.

## Scope Of This Guide

This guide explains the meaningful project files.

Excluded from detailed coverage:

- `venv/`
- `node_modules/`
- `__pycache__/`
- `frontend/dist/`

Those are generated or third-party files.

## Root Files

### `README.md`

- Main project overview, stack, features, and architecture.

### `00_READ_ME_FIRST.md`

- First-read onboarding document.

### `QUICK_START.md`

- Fast setup/run instructions.

### `QUICK_FIX_REFERENCE.md`

- Troubleshooting notes.

### `IMPLEMENTATION_ROADMAP.md`

- Planned build phases or roadmap.

### `IMPLEMENTATION_SUMMARY.md`

- High-level implementation summary.

### `FINAL_SUMMARY.md`

- Final project wrap-up document.

### `PROJECT_ANALYSIS_REPORT.md`

- Analysis-focused project review.

### `BUSINESS_STRATEGY_GUIDE.md`

- Product/business explanation for pitch or planning.

### `LAYOUT_GUIDE.md`

- Layout or UI structure guidance.

### `SYMPTOM_MATCHING_GUIDE.md`

- Symptom-to-medicine mapping explanation.

### `DOCTOR_FEATURES_DOCUMENTATION.md`

- Doctor module documentation.

### `DOCTOR_INTEGRATION_GUIDE.md`

- How doctor features fit into the full system.

### `__init__.py`

- Marks the root package.

## Backend Top-Level Files

### `backend/main.py`

- Main FastAPI entry point.
- Creates the app, enables CORS, includes routers, configures Socket.IO, initializes DB, and indexes products on startup.

### `backend/init_db.py`

- Database initialization helper script.

### `backend/migrate_to_mysql.py`

- Migration helper for moving toward MySQL-backed persistence.

### `backend/mock_warehouse.py`

- Mock warehouse/fulfillment helper for testing order flow.

### `backend/requirements.txt`

- Python dependencies for the backend.

### `backend/README.md`

- Backend-specific setup and notes.

### `backend/MYSQL_SETUP.md`

- MySQL setup instructions.

### `backend/test_db_connection.py`

- Simple DB connection verification script.

### `backend/users_database.json`

- Legacy/lightweight user storage artifact.

### `backend/order_history.json`

- Order history storage used by decision flow memory.

### `backend/pharmacist_requests.json`

- Stores pharmacist request/approval data.

### `backend/report_sessions.json`

- Stores temporary report-analysis sessions for follow-up Q&A.

## Backend Core Files

### `backend/app/core/config.py`

- Loads environment configuration like API keys.

### `backend/app/core/database.py`

- Creates SQLAlchemy engine/session.
- Exposes `get_db()`.
- Exposes `init_db()` and ensures some missing columns are added.

### `backend/app/core/models.py`

- Main SQLAlchemy models:
  - `User`
  - `Product`
  - `Order`
  - `OrderItem`
  - `Reminder`
  - `ChatHistory`
  - `DeliveryBoy`

### `backend/app/core/doctor_models.py`

- Doctor-specific SQLAlchemy models:
  - `DoctorTable`
  - `DoctorRegistrationRequest`
  - `AppointmentRequestTable`
  - `RevenueTable`

### `backend/app/core/security.py`

- Password hashing and verification helpers.

### `backend/app/core/langfuse_client.py`

- Langfuse tracing/observability integration.

## Backend API Files

### `backend/app/api/auth.py`

- User auth, password reset, profile update, pharmacist request, and manager approval routes.

### `backend/app/api/chat.py`

- Main AI chat route.
- Connects memory, translation, conversational parsing, and decision logic.

### `backend/app/api/products.py`

- Product browsing and admin inventory routes.

### `backend/app/api/orders.py`

- Order creation, cancellation, admin status, and analytics routes.

### `backend/app/api/patients.py`

- Patient history route.

### `backend/app/api/refill.py`

- Refill alerts, WhatsApp reminders, and reminder scheduling routes.

### `backend/app/api/report.py`

- Report upload analysis and report follow-up chat routes.

### `backend/app/api/nearby.py`

- Nearby shop, geocode, reverse-geocode, and routing routes.

### `backend/app/api/doctor.py`

- Doctor registration/login, approvals, appointments, revenue, and doctor listing routes.

### `backend/app/api/delivery.py`

- Delivery staff registration/login, approvals, assigned orders, completion, and cancellation routes.

### `backend/app/api/__init__.py`

- Marks the API package.

## Backend Agent Files

### `backend/app/agents/conversational_agent.py`

- Uses Groq LLM to convert raw text into structured JSON like intent, symptom, product, and quantity.

### `backend/app/agents/decision_agent.py`

- Main orchestration brain.
- Handles greetings, order follow-ups, pending orders, recommendation memory, symptom checks, and safety-driven routing.

### `backend/app/agents/execution_agent.py`

- Executes actions such as product lookup, stock checks, symptom recommendation ranking, order creation, and notifications.

### `backend/app/agents/safety_agent.py`

- Safety layer for risky medical or ordering situations.

### `backend/app/agents/guardrail.py`

- Validates LLM output quality/shape.

### `backend/app/agents/memory.py`

- Session memory helper for chat context.

### `backend/app/agents/refill_agent.py`

- Refill-focused intelligent helper.

### `backend/app/agents/__init__.py`

- Marks the agents package.

## Backend Service Files

### `backend/app/services/user_service.py`

- User business logic.

### `backend/app/services/product_service.py`

- Product retrieval, inventory, and stock logic.

### `backend/app/services/order_service.py`

- Order creation and order analytics logic.

### `backend/app/services/history_service.py`

- User/order/chat history helper logic.

### `backend/app/services/doctor_service.py`

- Doctor approval, appointment, and revenue logic.

### `backend/app/services/delivery_service.py`

- Delivery assignment, status, OTP completion, and cancellation logic.

### `backend/app/services/symptom_mapping.py`

- Symptom normalization and medicine recommendation rules.
- One of the most domain-important files.

### `backend/app/services/language_detector.py`

- Detects user language.

### `backend/app/services/translation_service.py`

- Translates text and can simplify English output.

### `backend/app/services/vector_store.py`

- ChromaDB collection access, product indexing, and semantic search.

### `backend/app/services/whatsapp_service.py`

- Twilio WhatsApp integration for alerts and reminders.

### `backend/app/services/database_service.py`

- Lower-level CRUD and analytics helper module for DB operations.

### `backend/app/services/Untitled-1.html`

- Temporary/demo artifact, not part of the core backend architecture.

## Backend Pydantic Model Files

### `backend/app/models/user.py`

- Request/response schemas for users and auth.

### `backend/app/models/doctor.py`

- Schemas for doctor registration, appointments, revenue, and dashboard data.

### `backend/app/models/delivery.py`

- Schemas for delivery registration, approval, and order actions.

### `backend/app/models/order.py`

- Order-related schema container.

### `backend/app/models/patient.py`

- Patient-related schema container.

### `backend/app/models/product.py`

- Currently contains upload route-style logic in a model folder, so this file is a cleanup opportunity.

## Backend Test Files

### `backend/tests/test_auth.py`

- Tests user/admin auth flows.

### `backend/tests/test_admin_products.py`

- Tests admin product routes.

### `backend/tests/test_conversational_agent.py`

- Tests message parsing behavior.

### `backend/tests/test_execution_agent_hybrid.py`

- Tests hybrid symptom-product ranking behavior.

### `backend/tests/test_execution_flow.py`

- Tests broader execution flow.

### `backend/tests/test_notifications.py`

- Tests notification behavior and fallback cases.

### `backend/tests/test_pending_order.py`

- Tests follow-up order context like quantity clarification.

### `backend/tests/test_safety_agent_manual.py`

- Manual-style safety validation tests.

### `backend/tests/test_symptom_mapping.py`

- Tests symptom mapping and language detection logic.

### `backend/tests/__init__.py`

- Marks the tests package.

## Frontend Top-Level Files

### `frontend/package.json`

- Frontend scripts and dependency configuration.

### `frontend/package-lock.json`

- Exact frontend dependency lockfile.

### `frontend/vite.config.js`

- Vite dev/build configuration.

### `frontend/eslint.config.js`

- Lint rules.

### `frontend/index.html`

- Main Vite HTML entry.

### `frontend/public/vite.svg`

- Static asset.

### `frontend/README.md`

- Frontend guide.

### `frontend/SUMMARY.md`

- Frontend summary document.

### `frontend/COMPLETION_SUMMARY.md`

- Delivery summary for frontend work.

### `frontend/REFACTORING_GUIDE.md`

- Refactor explanation and migration notes.

### `frontend/README_REFACTORING.md`

- Companion refactor documentation.

### `frontend/FOLDER_STRUCTURE_GUIDE.md`

- Recommended frontend structure guide.

### `frontend/DEPLOYMENT_GUIDE.md`

- Deployment instructions.

### `frontend/QUICK_REFERENCE.md`

- Quick lookup guide.

### `frontend/IMPLEMENTATION_TRACKER.md`

- Checklist/tracker file.

### `frontend/LOGIN_PAGE_*`

- A group of docs dedicated to login-page setup, examples, visuals, and summary.

## Frontend Source Files

### `frontend/src/main.jsx`

- React entry point that mounts the app.

### `frontend/src/index.css`

- Global styles.

### `frontend/src/App.jsx`

- Main application UI and the largest frontend file.
- Handles chat, ordering, reports, maps, role-based views, and admin sections.

### `frontend/src/App.css`

- Main app styling.

### `frontend/src/App.refactored.jsx`

- Cleaner refactored version of the main app.

### `frontend/src/App.jsx.bak`

- Backup copy of an older app file.

### `frontend/src/assets/react.svg`

- Default asset.

### `frontend/src/pages/LoginPage.jsx`

- Dedicated login page component.

### `frontend/src/styles/LoginPage.css`

- Login page styling.

## Frontend Components

### `frontend/src/components/DoctorRegistration.jsx`

- Doctor registration UI.

### `frontend/src/components/DoctorDashboard.jsx`

- Doctor dashboard UI.

### `frontend/src/components/AppointmentRequests.jsx`

- Pending appointment management UI.

### `frontend/src/components/AppointmentHistory.jsx`

- Appointment history UI.

### `frontend/src/components/RevenueAnalytics.jsx`

- Doctor revenue analytics UI.

### `frontend/src/components/BookAppointment.jsx`

- Patient appointment booking UI.

### `frontend/src/components/SystemManagerDoctorApprovals.jsx`

- Doctor approval screen for system manager.

### `frontend/src/components/SystemManagerRequestHistory.jsx`

- Request history screen for the system manager.

### `frontend/src/components/DeliveryBoyDashboard.jsx`

- Delivery staff dashboard.

## Best Files To Study First

1. `README.md`
2. `backend/main.py`
3. `backend/app/api/chat.py`
4. `backend/app/agents/conversational_agent.py`
5. `backend/app/agents/decision_agent.py`
6. `backend/app/agents/execution_agent.py`
7. `backend/app/services/symptom_mapping.py`
8. `backend/app/core/models.py`
9. `backend/app/api/doctor.py`
10. `frontend/src/App.jsx`

## Final Summary

This is a full-stack healthcare workflow platform, not just a medicine ordering app. The strongest parts of the codebase are the AI chat pipeline, symptom assistance, report analysis, doctor workflow, and delivery workflow.
