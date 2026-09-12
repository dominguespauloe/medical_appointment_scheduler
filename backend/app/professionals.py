from typing import Optional

from app.db import get_connection
from app.schemas import Professional


def load_professionals() -> list[Professional]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, name, speciality FROM professionals ORDER BY name"
        ).fetchall()
    return [Professional(id=r["id"], name=r["name"], speciality=r["speciality"]) for r in rows]


def find_professional(
    professionals: list[Professional],
    professional_id: Optional[str] = None,
    name: Optional[str] = None,
) -> Optional[Professional]:
    if professional_id:
        match = next((p for p in professionals if p.id == professional_id), None)
        if match:
            return match
    if name:
        return next((p for p in professionals if p.name.lower() == name.lower()), None)
    return None
