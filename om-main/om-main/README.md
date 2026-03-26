# Agentic Pharmacy Platform

This project is a full-stack pharmacy and healthcare platform built with:

- `FastAPI` for the backend API
- `React + Vite` for the frontend
- `MySQL + SQLAlchemy` for persistent storage
- `Groq LLMs + LangChain` for conversational understanding
- `ChromaDB` for product search/indexing
- `Socket.IO` for real-time order updates
- `Twilio WhatsApp` for notifications and reminders

It is more than a medicine ordering app. It combines:

- AI chat for medicine and symptom queries
- medicine ordering and order tracking
- refill reminders
- report analysis from uploaded report images
- nearby medical shop lookup with routing
- pharmacist/admin inventory management
- doctor registration, approval, appointments, and revenue tracking
- delivery staff approval and delivery completion with OTP

## What The Project Does

The main goal is to help a patient or pharmacy user interact with a pharmacy system in a natural way.

A user can:

- ask for medicine information
- describe symptoms and get mapped medicine suggestions
- place medicine orders through chat
- upload a prescription image for verification in some flows
- upload a medical report and ask questions about it
- view order history
- schedule refill reminders
- find nearby pharmacies
- book doctor appointments

Admins and managers can:

- manage products and upload inventory from Excel
- view order analytics
- approve pharmacist requests
- approve doctor registrations
- approve delivery staff registrations

Doctors can:

- register and wait for approval
- log in after approval
- manage appointment requests
- view revenue analytics

Delivery staff can:

- register and wait for approval
- view assigned orders
- complete deliveries using OTP verification

## High-Level Architecture

```text
Frontend (React/Vite)
    |
    | HTTP + Socket.IO
    v
Backend (FastAPI + Socket.IO ASGI)
    |
    +-- API routes
    +-- AI agents
    +-- business services
    +-- SQLAlchemy models
    +-- MySQL database
    +-- ChromaDB vector search
    +-- Twilio / external integrations
```

## Main Folders

```text
om-main/
  backend/
    main.py
    app/
      agents/      # AI decision, execution, safety, memory
      api/         # FastAPI routes
      core/        # DB config, ORM models, settings
      models/      # Pydantic request/response models
      services/    # business logic and integrations
    tests/

  frontend/
    src/
      components/  # dashboards and feature components
      pages/       # login page
      App.jsx      # main application UI
      main.jsx     # React entry point
```

## How The Backend Works

### Entry point

`backend/main.py` starts the FastAPI app, enables CORS, configures Socket.IO, initializes database tables, loads products, and indexes them into the vector store during startup.

### API modules

Important route groups:

- `/auth` - user login, registration, profile, password reset, pharmacist requests
- `/doctor` - doctor registration, approval, appointments, revenue, doctor listings
- `/delivery` - delivery staff registration, approval, assigned orders, completion
- `/chat` - main AI chatbot endpoint
- `/products` and `/admin/products` - product browsing and inventory update
- `/orders` and `/admin/orders` - ordering and admin order management
- `/refill` - refill alerts and WhatsApp reminders
- `/report` - medical report image analysis and report Q&A
- `/nearby` - pharmacy search, geocoding, reverse geocoding, routing
- `/patients` - patient order history

### Core data models

Main SQLAlchemy models in `backend/app/core/models.py`:

- `User`
- `Product`
- `Order`
- `OrderItem`
- `Reminder`
- `ChatHistory`
- `DeliveryBoy`

Doctor-specific tables live in `backend/app/core/doctor_models.py`.

### Service layer

Business logic is separated into services:

- `product_service.py` handles product loading, stock checks, Excel sync
- `order_service.py` handles order creation, status updates, analytics
- `user_service.py` handles auth and profile operations
- `doctor_service.py` handles doctor and appointment workflows
- `delivery_service.py` handles delivery workflows and OTP completion
- `whatsapp_service.py` sends or logs WhatsApp notifications
- `translation_service.py` handles multilingual translation support
- `symptom_mapping.py` maps symptoms to possible medicines
- `vector_store.py` indexes and searches product embeddings

## How The AI Chat Flow Works

The main AI flow is centered around the `/chat` endpoint.

### 1. Conversational parsing

File: `backend/app/agents/conversational_agent.py`

This file uses `ChatGroq` with a strict system prompt. It tries to convert the user message into structured JSON such as:

- intent
- product name
- symptom
- quantity
- missing fields
- friendly response

This is the first stage of understanding.

### 2. Memory and translation

File: `backend/app/api/chat.py`

The chat API:

- loads session memory
- translates non-English input to English if needed
- appends conversation history
- sends the enriched message to `parse_user_message`
- forwards the parsed result to the decision agent
- stores the final assistant reply back into memory
- translates the response back to the user language if needed

### 3. Decision agent

File: `backend/app/agents/decision_agent.py`

This is the brain of the chat workflow. It:

- handles greetings and small talk
- detects follow-up order messages like "book it"
- tracks pending orders per session
- remembers recent recommendations
- checks symptoms
- triggers prescription verification if needed
- calls the execution agent for actual work

### 4. Execution agent

File: `backend/app/agents/execution_agent.py`

This layer performs actions such as:

- product lookup
- symptom-based recommendations
- stock checks
- order execution
- notifications

### 5. Safety and guardrails

Files:

- `backend/app/agents/safety_agent.py`
- `backend/app/agents/guardrail.py`

These help validate risky actions such as prescription-required orders and LLM output quality.

## How The Frontend Works

The frontend is a React SPA.

- `frontend/src/main.jsx` mounts the app
- `frontend/src/App.jsx` contains the main application logic and most UI flows
- `frontend/src/pages/LoginPage.jsx` handles entry/login UI
- `frontend/src/components/` contains feature dashboards and modules

Frontend features include:

- role-based login and registration
- chat UI for AI assistant
- medicine browsing and search
- admin inventory and analytics dashboards
- doctor dashboards and booking components
- delivery dashboard
- nearby shop map flow using Leaflet
- multilingual UI content

## Special Features

### 1. Medical report analysis

`backend/app/api/report.py` accepts a report image, sends it to a Groq vision-capable model, extracts structured findings, stores temporary report sessions, and supports follow-up Q&A.

### 2. Symptom-to-medicine mapping

`backend/app/services/symptom_mapping.py` contains symptom normalization and medicine recommendation logic for symptom-based assistance.

### 3. Refill reminders

`backend/app/api/refill.py` and `refill_agent.py` support refill alerting and WhatsApp reminder scheduling.

### 4. Real-time updates

`Socket.IO` is configured in `backend/main.py` and used by the frontend for live order updates.

### 5. Nearby medical shops

`backend/app/api/nearby.py` provides nearby shops, geocoding, reverse geocoding, and routing support for map-based pharmacy discovery.

## Database And Startup Behavior

The backend expects a MySQL database.

`backend/app/core/database.py`:

- loads environment variables from `backend/.env`
- builds the MySQL connection URL
- creates the SQLAlchemy engine and session factory
- auto-creates tables
- tries to add missing columns for backward compatibility

On startup, `backend/main.py` also:

- initializes the DB
- loads product data
- indexes products into ChromaDB for semantic search

## Environment Variables

Create `backend/.env` for backend settings.

Typical variables used by this project:

```env
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=pharmacy_db

GROQ_API_KEY=your_groq_key
GROQ_CHAT_MODEL=llama-3.3-70b-versatile
GROQ_VISION_MODEL=meta-llama/llama-4-scout-17b-16e-instruct

OPENAI_API_KEY=optional
GOOGLE_API_KEY=optional

LANGFUSE_PUBLIC_KEY=optional
LANGFUSE_SECRET_KEY=optional
LANGFUSE_HOST=optional

TWILIO_ACCOUNT_SID=optional
TWILIO_AUTH_TOKEN=optional
TWILIO_WHATSAPP_FROM=optional

SYSTEM_MANAGER_ID=sysmanager
SYSTEM_MANAGER_PASSWORD=SysManager@123
```

Create `frontend/.env` if you want custom frontend endpoints:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_API_URL=http://127.0.0.1:8000
VITE_SOCKET_URL=http://127.0.0.1:8000
VITE_SYSTEM_MANAGER_ID=sysmanager
```

## How To Run The Project

### Backend

From `backend/`:

```bash
pip install -r requirements.txt
python init_db.py
uvicorn main:app --reload
```

Backend default URL:

```text
http://127.0.0.1:8000
```

### Frontend

From `frontend/`:

```bash
npm install
npm run dev
```

Frontend default URL:

```text
http://127.0.0.1:5173
```

## Useful Files To Read First

- `backend/main.py` - backend startup and router registration
- `backend/app/api/chat.py` - main chatbot endpoint
- `backend/app/agents/conversational_agent.py` - message parsing with LLM
- `backend/app/agents/decision_agent.py` - decision logic
- `backend/app/agents/execution_agent.py` - action execution
- `backend/app/core/models.py` - main database models
- `frontend/src/App.jsx` - main frontend UI flow
- `frontend/src/main.jsx` - React entry point

## Existing Documentation In The Repo

The repository already includes additional docs for specific modules:

- `QUICK_START.md`
- `IMPLEMENTATION_SUMMARY.md`
- `DOCTOR_INTEGRATION_GUIDE.md`
- `DOCTOR_FEATURES_DOCUMENTATION.md`
- `PROJECT_ANALYSIS_REPORT.md`
- `backend/MYSQL_SETUP.md`

## Notes And Current Reality

- `frontend/src/App.jsx` is very large and currently acts as the main UI controller.
- Some features use JSON files alongside the database for temporary or historical data.
- The backend router layout is clean, but some feature logic is still spread across agents and services.
- This project looks like an actively evolving prototype/product rather than a heavily polished production codebase.

## Short Project Explanation

If you want to explain this project simply:

> This is an AI-powered pharmacy management and healthcare assistance platform. It lets users chat with an AI assistant to ask about medicines, symptoms, orders, and medical reports, while also supporting pharmacy inventory, doctor appointments, delivery workflows, reminders, and nearby shop discovery through a React frontend and FastAPI backend.
