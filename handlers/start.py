import logging

from aiogram import Router, types
from aiogram.filters import CommandStart

from config import SCHOOL_NAME
from database import get_user
from handlers.keyboards import main_menu_keyboard

router = Router()
logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def cmd_start(message: types.Message) -> None:
    user = await get_user(message.from_user.id)
    kb = main_menu_keyboard()

    if user:
        # id, telegram_id, ism, familiya, til, telefon, sana
        await message.answer(
            f"👋 Sálem, <b>{user[2]} {user[3]}</b>!\n\n"
            f"✅ Siz burın demo imtixanǵa registraciyadan ótkensiz.\n\n"
            f"👤 Atı: <b>{user[2]}</b>\n"
            f"👤 Familiyası: <b>{user[3]}</b>\n"
            f"🌐 Til: <b>{user[4]}</b>\n"
            f"📞 Telefon: <b>{user[5]}</b>\n\n"
            f"Qosımsha maǵlıwmat alıw ushın tómendegi túymelerdi basıń 👇",
            reply_markup=kb,
            parse_mode="HTML",
        )
    else:
        await message.answer(
            f"🏫 <b>Sálem!</b>\n\n"
            f"<b>{SCHOOL_NAME}</b>\n"
            f"ushın demo imtixanǵa xosh kelipsiź!\n\n"
            f"Demo imtixanǵa qatnasıw ushın aldin registraciyadan ótiwińiz kerek.\n\n"
            f"Tómendegi túymeni basıń 👇",
            reply_markup=kb,
            parse_mode="HTML",
        )
        logger.info(f"New user started: {message.from_user.id} (@{message.from_user.username})")
