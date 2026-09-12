from typing import Optional, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

from app import appointments
from app.llm import get_structured_llm
from app.messages import (
    cancel_not_found_message,
    cancel_success_message,
    missing_fields_message,
    professional_not_found_message,
    schedule_conflict_message,
    schedule_success_message,
    unknown_message,
)
from app.professionals import find_professional, load_professionals
from app.prompts import build_system_prompt, build_user_prompt
from app.schemas import Appointment, IntentData, Professional

REQUIRED_FIELDS = ["professionalId", "datetime", "patientName"]


class IntentState(TypedDict, total=False):
    question: str
    professionals: list[Professional]
    data: IntentData
    missing_fields: list[str]
    professional: Optional[Professional]
    status: str
    message: str
    appointment: Optional[Appointment]


def load_professionals_node(state: IntentState) -> dict:
    return {"professionals": load_professionals()}


def classify_intent_node(state: IntentState) -> dict:
    llm = get_structured_llm()
    data = llm.invoke(
        [
            SystemMessage(content=build_system_prompt(state["professionals"])),
            HumanMessage(content=build_user_prompt(state["question"])),
        ]
    )
    return {"data": data}


def validate_fields_node(state: IntentState) -> dict:
    data = state["data"]
    missing = [f for f in REQUIRED_FIELDS if not getattr(data, f)]
    return {"missing_fields": missing}


def find_professional_node(state: IntentState) -> dict:
    professional = find_professional(state["professionals"], professional_id=state["data"].professionalId)
    return {"professional": professional}


def schedule_node(state: IntentState) -> dict:
    data = state["data"]
    professional = state["professional"]
    appt = appointments.schedule(
        professional_id=professional.id,
        professional_name=professional.name,
        dt=data.datetime,
        patient_name=data.patientName,
        reason=data.reason,
    )
    if appt is None:
        return {"status": "error", "message": schedule_conflict_message()}
    return {
        "status": "success",
        "message": schedule_success_message(professional.name, data.datetime, data.patientName),
        "appointment": appt,
    }


def cancel_node(state: IntentState) -> dict:
    data = state["data"]
    professional = state["professional"]
    appt = appointments.cancel(professional_id=professional.id, dt=data.datetime, patient_name=data.patientName)
    if appt is None:
        return {"status": "error", "message": cancel_not_found_message()}
    return {
        "status": "success",
        "message": cancel_success_message(professional.name, data.datetime),
        "appointment": appt,
    }


def unknown_node(state: IntentState) -> dict:
    return {"status": "info", "message": unknown_message()}


def missing_fields_node(state: IntentState) -> dict:
    return {"status": "error", "message": missing_fields_message(state["missing_fields"])}


def professional_not_found_node(state: IntentState) -> dict:
    return {"status": "error", "message": professional_not_found_message()}


def route_after_classify(state: IntentState) -> str:
    return "unknown" if state["data"].intent == "unknown" else "validate_fields"


def route_after_validate(state: IntentState) -> str:
    return "missing_fields" if state["missing_fields"] else "find_professional"


def route_after_find_professional(state: IntentState) -> str:
    if not state["professional"]:
        return "professional_not_found"
    return state["data"].intent


def build_graph():
    builder = StateGraph(IntentState)
    builder.add_node("load_professionals", load_professionals_node)
    builder.add_node("classify_intent", classify_intent_node)
    builder.add_node("validate_fields", validate_fields_node)
    builder.add_node("find_professional", find_professional_node)
    builder.add_node("schedule", schedule_node)
    builder.add_node("cancel", cancel_node)
    builder.add_node("unknown", unknown_node)
    builder.add_node("missing_fields", missing_fields_node)
    builder.add_node("professional_not_found", professional_not_found_node)

    builder.add_edge(START, "load_professionals")
    builder.add_edge("load_professionals", "classify_intent")
    builder.add_conditional_edges(
        "classify_intent",
        route_after_classify,
        {"unknown": "unknown", "validate_fields": "validate_fields"},
    )
    builder.add_conditional_edges(
        "validate_fields",
        route_after_validate,
        {"missing_fields": "missing_fields", "find_professional": "find_professional"},
    )
    builder.add_conditional_edges(
        "find_professional",
        route_after_find_professional,
        {
            "professional_not_found": "professional_not_found",
            "schedule": "schedule",
            "cancel": "cancel",
        },
    )
    builder.add_edge("schedule", END)
    builder.add_edge("cancel", END)
    builder.add_edge("unknown", END)
    builder.add_edge("missing_fields", END)
    builder.add_edge("professional_not_found", END)

    return builder.compile()


intent_graph = build_graph()


def run_intent_graph(question: str) -> IntentState:
    return intent_graph.invoke({"question": question})
