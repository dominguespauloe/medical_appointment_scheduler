import json
from datetime import datetime, timezone

from app.schemas import Professional


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def build_system_prompt(professionals: list[Professional]) -> str:
    payload = {
        "role": "Intent Classifier for Medical Appointments",
        "task": "Identify user intent and extract all appointment-related details",
        "professionals": [
            {"id": p.id, "name": p.name, "specialty": p.speciality} for p in professionals
        ],
        "current_date": _now_iso(),
        "rules": {
            "schedule": {
                "description": "User wants to book/schedule a new appointment",
                "keywords": ["schedule", "book", "appointment", "I want to", "make an appointment"],
                "required_fields": ["professionalId", "datetime", "patientName"],
                "optional_fields": ["reason"],
            },
            "cancel": {
                "description": "User wants to cancel an existing appointment",
                "keywords": ["cancel", "remove", "delete", "cancel my appointment"],
                "required_fields": ["professionalId", "datetime", "patientName"],
            },
            "unknown": {
                "description": "Anything not related to scheduling or cancelling appointments",
                "examples": ["weather questions", "general info", "unrelated queries"],
            },
        },
        "guidelines": {
            "language": "Use simple, non-technical language",
            "format": "Clear and concise, avoid jargon",
            "personalization": "Include relevant details (names, dates, times)",
            "empathy": "Acknowledge patient emotions, especially for errors",
        },
        "scenarios": {
            "schedule_success": "Confirm the appointment with all details",
            "schedule_error": "Apologize and explain why scheduling failed",
            "cancel_success": "Confirm the cancellation",
            "cancel_error": "Apologize and explain why cancellation failed",
            "unknown": "Politely explain you can only help with appointments",
        },
        "scenarios_examples": {
            "schedule_success": (
                "Sua consulta com o Dr. Alicio da Silva em 12 de fevereiro de 2026 às 16h "
                "foi confirmada para Maria Santos. Aguardamos sua visita!"
            ),
            "schedule_error": (
                "Peço desculpas, mas esse horário já está reservado. Por favor, tente outro "
                "horário ou entre em contato conosco para verificar a disponibilidade."
            ),
            "cancel_success": (
                "Sua consulta com o Dr. Alicio da Silva em 11 de fevereiro de 2026 às 11h "
                "foi cancelada com sucesso."
            ),
            "cancel_error": (
                "Não encontrei nenhuma consulta com essas informações. Por favor, verifique "
                "a data, o horário e o nome do médico."
            ),
            "unknown": (
                "Posso ajudá-lo(a) a agendar ou cancelar consultas médicas. Como posso "
                "ajudá-lo(a) com sua consulta hoje?"
            ),
        },
        "extraction_instructions": {
            "professionalId": (
                "Match the professional name mentioned in the question to the ID from the "
                "professionals list. Use fuzzy matching."
            ),
            "professionalName": "Extract the professional name as mentioned by the user",
            "datetime": (
                "Parse relative dates (today, tomorrow) and times. Convert to ISO format. "
                "Use current_date as reference."
            ),
            "patientName": "Extract the patient name from the question or context",
            "reason": "Extract the reason/purpose for the appointment (only for scheduling)",
        },
        "examples": [
            {
                "input": "I want to schedule with Dr. Carlos Silva for tomorrow at 4pm for a check-up",
                "output": {
                    "intent": "schedule",
                    "professionalId": "MED-001",
                    "professionalName": "Dr. Carlos Silva",
                    "datetime": "2026-02-12T16:00:00.000Z",
                    "reason": "check-up",
                },
            },
            {
                "input": "Cancel my appointment with Dr. Ana Souza today at 11am",
                "output": {
                    "intent": "cancel",
                    "professionalId": "MED-002",
                    "professionalName": "Dr. Ana Souza",
                    "datetime": "2026-02-11T11:00:00.000Z",
                },
            },
            {
                "input": "What is the weather today?",
                "output": {"intent": "unknown"},
            },
        ],
    }
    return json.dumps(payload, ensure_ascii=False)


def build_user_prompt(question: str) -> str:
    payload = {
        "question": question,
        "instructions": [
            "Carefully analyze the question to determine the user intent",
            "Extract all relevant appointment details",
            "Convert dates and times to ISO format",
            "Match professional names to their IDs",
            "Return only the fields that are present in the question",
        ],
    }
    return json.dumps(payload, ensure_ascii=False)
