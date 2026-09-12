from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app import appointments
from app.db import init_db
from app.graph import run_intent_graph
from app.professionals import load_professionals
from app.schemas import Appointment, ChatRequest, ChatResponse, Professional

init_db()

app = FastAPI(title="Medical Appointment Intent API")


# allowed origins (ports where your frontend runs)
origins = [
    "http://localhost:3000",      # React default port
    "http://localhost:5173",      # Vite default port
    "http://localhost:5174",      # Vite secundary default port
    "http://localhost:8080",      # Vue/Angular default port
    "http://127.0.0.1:3000",      # Loopback IP format
]

app.add_middleware(
    CORSMiddleware,
    # allow_origins=[FRONTEND_ORIGIN],
    allow_origins=origins,           # List of allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/professionals", response_model=list[Professional])
def get_professionals() -> list[Professional]:
    return load_professionals()


@app.get("/api/appointments", response_model=list[Appointment])
def get_appointments() -> list[Appointment]:
    return appointments.list_appointments()


@app.post("/api/intent", response_model=ChatResponse)
def identify_intent(req: ChatRequest) -> ChatResponse:
    try:
        result = run_intent_graph(req.question)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001 - surface upstream LLM/provider errors to the client
        raise HTTPException(status_code=502, detail=f"LLM request failed: {exc}") from exc

    return ChatResponse(
        intent=result["data"].intent,
        status=result["status"],
        message=result["message"],
        data=result["data"],
        appointment=result.get("appointment"),
    )
