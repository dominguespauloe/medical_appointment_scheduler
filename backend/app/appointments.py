import sqlite3
from typing import Optional

from app.db import get_connection
from app.schemas import Appointment

_SELECT_COLUMNS = "professional_id, professional_name, datetime, patient_name, reason"


def _row_to_appointment(row: sqlite3.Row) -> Appointment:
    return Appointment(
        professionalId=row["professional_id"],
        professionalName=row["professional_name"],
        datetime=row["datetime"],
        patientName=row["patient_name"],
        reason=row["reason"],
    )


def list_appointments() -> list[Appointment]:
    with get_connection() as conn:
        rows = conn.execute(
            f"SELECT {_SELECT_COLUMNS} FROM appointments ORDER BY datetime"
        ).fetchall()
    return [_row_to_appointment(r) for r in rows]


def find_conflict(professional_id: str, dt: str) -> Optional[Appointment]:
    with get_connection() as conn:
        row = conn.execute(
            f"SELECT {_SELECT_COLUMNS} FROM appointments WHERE professional_id = ? AND datetime = ?",
            (professional_id, dt),
        ).fetchone()
    return _row_to_appointment(row) if row else None


def schedule(
    professional_id: str, professional_name: str, dt: str, patient_name: str, reason: Optional[str]
) -> Optional[Appointment]:
    with get_connection() as conn:
        try:
            conn.execute(
                "INSERT INTO appointments (professional_id, professional_name, datetime, patient_name, reason) "
                "VALUES (?, ?, ?, ?, ?)",
                (professional_id, professional_name, dt, patient_name, reason),
            )
        except sqlite3.IntegrityError:
            return None
    return Appointment(
        professionalId=professional_id,
        professionalName=professional_name,
        datetime=dt,
        patientName=patient_name,
        reason=reason,
    )


def cancel(professional_id: str, dt: str, patient_name: Optional[str] = None) -> Optional[Appointment]:
    with get_connection() as conn:
        row = conn.execute(
            f"SELECT {_SELECT_COLUMNS} FROM appointments WHERE professional_id = ? AND datetime = ?",
            (professional_id, dt),
        ).fetchone()
        if row is None:
            return None
        if patient_name and row["patient_name"].lower() != patient_name.lower():
            return None
        conn.execute(
            "DELETE FROM appointments WHERE professional_id = ? AND datetime = ?",
            (professional_id, dt),
        )
    return _row_to_appointment(row)
