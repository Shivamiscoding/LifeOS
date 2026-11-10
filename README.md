# LifeOS

LifeOS is a personal operating system for tasks, projects, calendar blocks, files, automations, insights, and natural-language commands.

## Run locally

Backend (Python 3.11+ recommended):

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server proxies `/api` to `http://127.0.0.1:8000`. SQLite is used by default, and tables are created on first startup. Set `AI_PROVIDER=bharatcode` and provide `BHARATCODE_API_KEY` to use the real model provider; the default `mock` provider is safe for local development and clearly keeps actions inside the application database.

## API

The FastAPI contract is available at `/docs`. Private endpoints use a bearer token returned by `/api/v1/auth/login/` or `/api/v1/auth/register/`. All task, project, calendar, file, automation, AI, and insight queries are scoped to the authenticated user.

Supported upload types are PDF, DOCX, TXT, and CSV. Files are stored under the configured `UPLOAD_DIR` and are limited by `MAX_UPLOAD_SIZE_MB`.
