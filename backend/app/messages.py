from datetime import datetime

_MONTHS_PT = [
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
]

_FIELD_LABELS_PT = {
    "professionalId": "o profissional",
    "datetime": "a data e o horário",
    "patientName": "o nome do paciente",
}


def format_datetime_ptbr(iso_str: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    except ValueError:
        return iso_str
    time_part = f"{dt.hour}h" if dt.minute == 0 else f"{dt.hour}h{dt.minute:02d}"
    return f"{dt.day} de {_MONTHS_PT[dt.month - 1]} de {dt.year} às {time_part}"


def missing_fields_message(missing: list[str]) -> str:
    labels = ", ".join(_FIELD_LABELS_PT.get(f, f) for f in missing)
    return f"Para continuar, preciso que me informe {labels}."


def professional_not_found_message() -> str:
    return "Não encontrei esse profissional em nossa lista. Por favor, verifique o nome e tente novamente."


def schedule_success_message(professional_name: str, dt_iso: str, patient_name: str) -> str:
    return (
        f"Sua consulta com {professional_name} em {format_datetime_ptbr(dt_iso)} foi "
        f"confirmada para {patient_name}. Aguardamos sua visita!"
    )


def schedule_conflict_message() -> str:
    return (
        "Peço desculpas, mas esse horário já está reservado. Por favor, tente outro "
        "horário ou entre em contato conosco para verificar a disponibilidade."
    )


def cancel_success_message(professional_name: str, dt_iso: str) -> str:
    return f"Sua consulta com {professional_name} em {format_datetime_ptbr(dt_iso)} foi cancelada com sucesso."


def cancel_not_found_message() -> str:
    return (
        "Não encontrei nenhuma consulta com essas informações. Por favor, verifique a "
        "data, o horário e o nome do médico."
    )


def unknown_message() -> str:
    return "Posso ajudá-lo(a) a agendar ou cancelar consultas médicas. Como posso ajudá-lo(a) com sua consulta hoje?"
