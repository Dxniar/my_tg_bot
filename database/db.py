from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import aiosqlite


@dataclass
class Registration:
    id: int
    user_id: int
    full_name: str
    phone: str
    email: str
    company: str
    position: str
    city: str
    consent: int
    created_at: str


class Database:
    def __init__(self, db_path: Path):
        self.db_path = db_path

    async def init(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS registrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL UNIQUE,
                    full_name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    email TEXT NOT NULL,
                    company TEXT NOT NULL,
                    position TEXT NOT NULL,
                    city TEXT NOT NULL,
                    consent INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    reminder_type TEXT NOT NULL,
                    scheduled_for TEXT NOT NULL,
                    sent INTEGER NOT NULL DEFAULT 0,
                    UNIQUE(user_id, reminder_type)
                );
                """
            )
            await db.commit()

    async def add_registration(
        self,
        user_id: int,
        full_name: str,
        phone: str,
        email: str,
        company: str,
        position: str,
        city: str,
        consent: bool,
    ) -> int:
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO registrations (
                    user_id, full_name, phone, email, company, position, city, consent, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (user_id, full_name, phone, email, company, position, city, int(consent), now),
            )
            await db.commit()
            return cursor.lastrowid

    async def get_registration_by_user(self, user_id: int) -> Registration | None:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT id, user_id, full_name, phone, email, company, position, city, consent, created_at "
                "FROM registrations WHERE user_id = ?",
                (user_id,),
            )
            row = await cursor.fetchone()
            if not row:
                return None
            return Registration(*row)

    async def count_registrations(self) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM registrations")
            row = await cursor.fetchone()
            return int(row[0])

    async def get_latest_registrations(self, limit: int = 10) -> list[Registration]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                SELECT id, user_id, full_name, phone, email, company, position, city, consent, created_at
                FROM registrations
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            )
            rows = await cursor.fetchall()
            return [Registration(*row) for row in rows]

    async def get_all_registrations(self) -> list[Registration]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                SELECT id, user_id, full_name, phone, email, company, position, city, consent, created_at
                FROM registrations
                ORDER BY id ASC
                """
            )
            rows = await cursor.fetchall()
            return [Registration(*row) for row in rows]

    async def upsert_reminder(self, user_id: int, reminder_type: str, scheduled_for: str) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO reminders (user_id, reminder_type, scheduled_for, sent)
                VALUES (?, ?, ?, 0)
                ON CONFLICT(user_id, reminder_type)
                DO UPDATE SET scheduled_for = excluded.scheduled_for, sent = 0
                """,
                (user_id, reminder_type, scheduled_for),
            )
            await db.commit()

    async def mark_reminder_sent(self, user_id: int, reminder_type: str) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE reminders SET sent = 1 WHERE user_id = ? AND reminder_type = ?",
                (user_id, reminder_type),
            )
            await db.commit()

    async def get_registered_user_ids(self) -> list[int]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT user_id FROM registrations")
            rows = await cursor.fetchall()
            return [int(row[0]) for row in rows]
