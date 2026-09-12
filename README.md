# Medical Appointment Intent App

Chat-style app that identifies a user's intent (schedule / cancel / unknown) for medical
appointments and extracts structured details from free-text questions, based on the logic in
[`template/identifyIntent.ts`](template/identifyIntent.ts) and the professionals list in
[`template/professionals.json`](template/professionals.json).

- **backend/** — FastAPI + LangChain + LangGraph + OpenRouter. The `/api/intent` request runs
  through a LangGraph `StateGraph` ([`app/graph.py`](backend/app/graph.py)): load professionals →
  classify intent (`with_structured_output`) → validate required fields → look up the
  professional → schedule/cancel (or an unknown/error node), each step as its own graph node/edge
  so a LangSmith trace shows the whole decision path. Scheduling/cancelling runs against a
  SQLite-backed store (`backend/data/app.db`, conflict detection included); the professionals
  list is also persisted in SQLite, seeded once from `backend/data/professionals.json` on first
  startup.
- **frontend/** — React + Vite + TypeScript chat UI. Shows the professionals list, live
  appointments, and the assistant's confirmation/error messages.


<img width="1078" height="949" alt="image" src="https://github.com/user-attachments/assets/de1359d5-01ca-4bdf-8b51-ce488b6c6524" />


## Backend setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your OPENROUTER_API_KEY
uvicorn app.main:app --reload --port 8000
```

<img width="1413" height="492" alt="image" src="https://github.com/user-attachments/assets/735bb411-4d9f-4af0-a860-bc3a79735129" />



## Frontend setup

```bash
cd frontend
npm install
cp .env.example .env   # VITE_API_BASE_URL, defaults to http://localhost:8000
npm run dev
```

Open http://localhost:5173. The frontend expects the backend on port 8000 by default
(configurable via `VITE_API_BASE_URL` / backend's `FRONTEND_ORIGIN` for CORS).

To inspect each LangGraph node/edge as a trace, set `LANGSMITH_API_KEY`,
`LANGCHAIN_TRACING_V2=true`, and `LANGCHAIN_PROJECT` in `backend/.env` (LangChain/LangGraph pick
these up automatically — no code changes needed) and view runs at https://smith.langchain.com.

## Running with Docker

Each app has its own `Dockerfile` (backend: Python/uvicorn; frontend: multi-stage Node build →
nginx serving the static bundle).

```bash
# Backend
cd backend
docker build -t medical-intent-backend .
docker run -d --name medical-backend -p 8000:8000 \
  -e OPENROUTER_API_KEY=your-key-here \
  -e OPENROUTER_MODEL=openai/gpt-4o-mini \
  -e FRONTEND_ORIGIN=http://localhost:5173 \
  -v "$(pwd)/data:/app/data" \
  medical-intent-backend

# Frontend (VITE_API_BASE_URL is baked in at build time)
cd ../frontend
docker build -t medical-intent-frontend --build-arg VITE_API_BASE_URL=http://localhost:8000 .
docker run -d --name medical-frontend -p 5173:80 medical-intent-frontend
```

Open http://localhost:5173. If you rebuild the frontend to point at a different backend URL,
pass a new `--build-arg VITE_API_BASE_URL=...` and rebuild the image.

The `-v "$(pwd)/data:/app/data"` mount on the backend persists `app.db` (and the
`professionals.json` seed) on the host across container restarts/rebuilds. Without it, the
SQLite file lives only inside the container's writable layer and is lost when the container is
removed.

## API

- `GET /api/professionals` — list of medical professionals (from SQLite)
- `GET /api/appointments` — current appointments (from SQLite)
- `POST /api/intent` — `{ "question": "..." }` → identifies intent, executes the
  schedule/cancel action, and returns a confirmation/error message plus the extracted data
