import aiosqlite
import logging
from typing import Optional

from config import DATABASE_PATH

logger = logging.getLogger(__name__)


async def create_tables() -> None:
    """Barcha kerakli jadvallarni yaratadi."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                ism         TEXT    NOT NULL,
                familiya    TEXT    NOT NULL,
                tuman       TEXT    NOT NULL,
                maktab      TEXT    NOT NULL,
                til         TEXT    NOT NULL,
                telefon     TEXT    NOT NULL,
                sana        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Eski bazaga yangi ustunlar qo'shish (migration)
        try:
            await db.execute("ALTER TABLE users ADD COLUMN tuman TEXT NOT NULL DEFAULT ''")
        except Exception:
            pass
        try:
            await db.execute("ALTER TABLE users ADD COLUMN maktab TEXT NOT NULL DEFAULT ''")
        except Exception:
            pass
        await db.commit()
    logger.info("✅ Database jadvallari tayyor.")


async def add_user(
    telegram_id: int,
    ism: str,
    familiya: str,
    tuman: str,
    maktab: str,
    til: str,
    telefon: str,
) -> bool:
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute(
                """
                INSERT INTO users (telegram_id, ism, familiya, tuman, maktab, til, telefon)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (telegram_id, ism, familiya, tuman, maktab, til, telefon),
            )
            await db.commit()
        return True
    except aiosqlite.IntegrityError:
        return False


async def get_user(telegram_id: int) -> Optional[tuple]:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return tuple(row) if row else None


async def get_all_users() -> list[tuple]:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users ORDER BY sana DESC"
        ) as cursor:
            rows = await cursor.fetchall()
            return [tuple(r) for r in rows]


async def get_users_count() -> int:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0
