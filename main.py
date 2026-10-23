"""Job Application Hunt Tracker - FastAPI + SQLite backend."""
import sqlite3
from contextlib import asynccontextmanager, contextmanager
from pathlib import Path
from typing import Literal, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "job_tracker.db"

Status = Literal["Applied", "Interviewing", "Offer", "Rejected"]


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                position_title TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Applied'
                    CHECK (status IN ('Applied', 'Interviewing', 'Offer', 'Rejected')),
                date_applied TEXT,
                salary_range TEXT,
                notes TEXT
            )
            """
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Job Application Hunt Tracker", lifespan=lifespan)


class ApplicationIn(BaseModel):
    company_name: str
    position_title: str
    status: Status = "Applied"
    date_applied: Optional[str] = None
    salary_range: Optional[str] = None
    notes: Optional[str] = None


class ApplicationUpdate(BaseModel):
    """All fields optional so a partial update (e.g. status only) works."""
    company_name: Optional[str] = None
    position_title: Optional[str] = None
    status: Optional[Status] = None
    date_applied: Optional[str] = None
    salary_range: Optional[str] = None
    notes: Optional[str] = None


def fetch_one(conn: sqlite3.Connection, app_id: int) -> dict:
    row = conn.execute("SELECT * FROM applications WHERE id = ?", (app_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return dict(row)


@app.get("/api/applications")
def list_applications():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM applications ORDER BY date_applied DESC, id DESC"
        ).fetchall()
    return [dict(r) for r in rows]


@app.post("/api/applications", status_code=201)
def create_application(item: ApplicationIn):
    with get_db() as conn:
        cur = conn.execute(
            """
            INSERT INTO applications
                (company_name, position_title, status, date_applied, salary_range, notes)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                item.company_name.strip(),
                item.position_title.strip(),
                item.status,
                item.date_applied,
                item.salary_range,
                item.notes,
            ),
        )
        return fetch_one(conn, cur.lastrowid)


@app.put("/api/applications/{app_id}")
def update_application(app_id: int, item: ApplicationUpdate):
    changes = item.model_dump(exclude_unset=True)
    with get_db() as conn:
        fetch_one(conn, app_id)  # 404 if missing
        if changes:
            assignments = ", ".join(f"{col} = ?" for col in changes)
            conn.execute(
                f"UPDATE applications SET {assignments} WHERE id = ?",
                (*changes.values(), app_id),
            )
        return fetch_one(conn, app_id)


@app.delete("/api/applications/{app_id}")
def delete_application(app_id: int):
    with get_db() as conn:
        fetch_one(conn, app_id)  # 404 if missing
        conn.execute("DELETE FROM applications WHERE id = ?", (app_id,))
    return {"deleted": app_id}


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(BASE_DIR / "index.html")
