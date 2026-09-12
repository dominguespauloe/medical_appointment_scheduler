import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DB_PATH = DATA_DIR / "app.db"
SEED_PATH = DATA_DIR / "professionals.json"


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS professionals (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                speciality TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                professional_id TEXT NOT NULL REFERENCES professionals(id),
                professional_name TEXT NOT NULL,
                datetime TEXT NOT NULL,
                patient_name TEXT NOT NULL,
                reason TEXT,
                UNIQUE (professional_id, datetime)
            )
            """
        )
        _seed_professionals(conn)


def _seed_professionals(conn: sqlite3.Connection) -> None:
    count = conn.execute("SELECT COUNT(*) FROM professionals").fetchone()[0]
    if count > 0 or not SEED_PATH.exists():
        return
    raw = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    conn.executemany(
        "INSERT INTO professionals (id, name, speciality) VALUES (?, ?, ?)",
        [(p["id"], p["Medical_name"], p["speciality"]) for p in raw],
    )
