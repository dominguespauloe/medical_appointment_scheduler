from typing import Literal, Optional

from pydantic import BaseModel, Field


class IntentData(BaseModel):
    """Extracted user intent and appointment details for a medical appointment request."""

    intent: Literal["schedule", "cancel", "unknown"] = Field(description="The user intent")
    professionalId: Optional[str] = Field(default=None, description="ID of the medical professional")
    professionalName: Optional[str] = Field(default=None, description="Name of the medical professional")
    datetime: Optional[str] = Field(default=None, description="Appointment date and time in ISO format")
    patientName: Optional[str] = Field(default=None, description="Patient name extracted from question")
    reason: Optional[str] = Field(default=None, description="Reason for appointment (for scheduling)")


class Professional(BaseModel):
    id: str
    name: str
    speciality: str


class Appointment(BaseModel):
    professionalId: str
    professionalName: str
    datetime: str
    patientName: str
    reason: Optional[str] = None


class ChatRequest(BaseModel):
    question: str = Field(min_length=1)


class ChatResponse(BaseModel):
    intent: Literal["schedule", "cancel", "unknown"]
    status: Literal["success", "error", "info"]
    message: str
    data: IntentData
    appointment: Optional[Appointment] = None
