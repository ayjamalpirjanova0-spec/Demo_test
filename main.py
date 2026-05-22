"""
Abu Ali ibn Sino atındaǵı qánigeleswirlengen mekteptiń Xojeli filialı
— Demo imtixan registraciya boti —

Run:
    python main.py
"""

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database import create_tables
from handlers import admin, info, registration, start


async def main() -> None:
    # ── Logging ──────────────────────────────────────────────────────────────
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )
    logger = logging.getLogger(__name__)
    logger.info("🚀 Bot ishga tushirilmoqda...")

    # ── Database ─────────────────────────────────────────────────────────────
    await create_tables()

    # ── Bot & Dispatcher ─────────────────────────────────────────────────────
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # ── Routers — ORDER MATTERS ───────────────────────────────────────────────
    # admin & info first (no state conflicts)
    dp.include_router(admin.router)
    dp.include_router(info.router)
    dp.include_router(registration.router)
    dp.include_router(start.router)

    # ── Start polling ─────────────────────────────────────────────────────────
    logger.info("✅ Bot tayyor, polling boshlandi...")
    try:
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
        )
    finally:
        await bot.session.close()
        logger.info("🛑 Bot to'xtatildi.")


if __name__ == "__main__":
    asyncio.run(main())
