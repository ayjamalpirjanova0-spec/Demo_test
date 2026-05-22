from aiogram import Router, types, F
from aiogram.filters import Command

from config import SCHOOL_NAME
from handlers.keyboards import main_menu_keyboard

router = Router()


INFO_TEXT = (
    "📌 <b>Demo imtixan haqqında maǵlıwmat</b>\n\n"
    "Bul demo imtixan bolıp, haqıyqıy kiriw imtixanı emes.\n\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "📚 <b>Imtixan quramı:</b>\n\n"
    "🔬 <b>30 test</b> — Science\n"
    "🌍 <b>15 test</b> — Inglis tili\n\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "🕐 <b>Waqıt:</b> Keyinnen xabarlanadı\n"
    "📍 <b>Orın:</b> Xojeli filialı\n\n"
    f"🏫 <i>{SCHOOL_NAME}</i>"
)


@router.message(F.text == "ℹ️ Maǵlıwmat")
async def show_info(message: types.Message) -> None:
    await message.answer(
        INFO_TEXT,
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML",
    )


@router.message(Command("info"))
async def cmd_info(message: types.Message) -> None:
    await message.answer(
        INFO_TEXT,
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML",
    )
