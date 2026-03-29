## Render Deployment

This backend is ready to deploy on Render as a web service.

### Start Command

Use:

`bash render-start.sh`

### Build Command

Use:

`pip install -r requirements.txt`

### Root Directory

Use:

`om-main/om-main/backend`

### Environment Variables

Required:

- `DATABASE_URL` or the `MYSQL_*` variables
- `SYSTEM_MANAGER_ID`
- `SYSTEM_MANAGER_PASSWORD`

Optional depending on features:

- `GROQ_API_KEY`
- `GROQ_CHAT_MODEL`
- `GROQ_VISION_MODEL`
- `OPENAI_API_KEY`
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_WHATSAPP_FROM`
- `LANGFUSE_PUBLIC_KEY`
- `LANGFUSE_SECRET_KEY`
- `LANGFUSE_HOST`
- `GOOGLE_API_KEY`

Notes:

- Render env vars now take priority over the local `.env`
- The app supports `DATABASE_URL` directly for hosted deployment
