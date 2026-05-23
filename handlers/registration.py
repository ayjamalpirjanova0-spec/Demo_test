import logging
import re

from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove

from database import add_user, get_user
from handlers.keyboards import (
    cancel_keyboard,
    language_keyboard,
    main_menu_keyboard,
    phone_keyboard,
)

router = Router()
logger = logging.getLogger(__name__)

LANG_OPTIONS = {"🇺🇿 Ózbek tili", "📖 Qaraqalpaq tili"}
CANCEL_TEXT = "❌ Biykarlaw"


# ─── FSM States ───────────────────────────────────────────────────────────────

class RegState(StatesGroup):
    ism      = State()
    familiya = State()
    til      = State()
    telefon  = State()


# ─── Helper ───────────────────────────────────────────────────────────────────

def normalize_phone(raw: str) -> str | None:
    """
    Telefon raqamini normallash.
    Raqamlar, +, bo'sh joylar va tire'larni qabul qiladi.
    Kamida 9 raqam bo'lishi kerak.
    """
    cleaned = re.sub(r"[\s\-()]", "", raw)
    if not re.match(r"^\+?\d{9,15}$", cleaned):
        return None
    if not cleaned.startswith("+"):
        cleaned = "+" + cleaned
    return cleaned


# ─── Cancel anytime ───────────────────────────────────────────────────────────

@router.message(
    StateFilter(RegState),
    F.text == CANCEL_TEXT,
)
async def cancel_registration(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "🚫 Registraciya biykar qılındı.\n\n"
        "Qaytadan baslaw ushın tómendegi túymeni basıń 👇",
        reply_markup=main_menu_keyboard(),
    )


# ─── Step 0 — trigger ─────────────────────────────────────────────────────────

@router.message(F.text == "📋 Registraciya")
async def start_registration(message: types.Message, state: FSMContext) -> None:
    # Already registered?
    user = await get_user(message.from_user.id)
    if user:
        await message.answer(
            "✅ <b>Siz burın registraciyadan ótkensiź!</b>\n\n"
            f"👤 Atı: <b>{user[2]}</b>\n"
            f"👤 Familiyası: <b>{user[3]}</b>\n"
            f"🌐 Til: <b>{user[4]}</b>\n"
            f"📞 Telefon: <b>{user[5]}</b>\n\n"
            f"📅 Sáne: <b>{user[6]}</b>",
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML",
        )
        return

    await state.set_state(RegState.ism)
    await message.answer(
        "📝 <b>Registraciya baslandı!</b>\n\n"
        "1️⃣  Atıńızdı kiritiń:\n"
        "<i>(Mısalı: Alibek)</i>",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML",
    )


# ─── Step 1 — ism ─────────────────────────────────────────────────────────────

@router.message(RegState.ism)
async def step_ism(message: types.Message, state: FSMContext) -> None:
    text = (message.text or "").strip()

    if len(text) < 2 or not re.match(r"^[A-Za-zА-Яа-яЁёÓóÁáÉéÍíÚúÑñQqWw'\- ]+$", text, re.UNICODE):
        await message.answer(
            "❌ Atıńızdı durıs kiritiń!\n"
            "<i>(Keminde 2 háripler, tek hárip bolıwı kerek)</i>",
            parse_mode="HTML",
        )
        return

    await state.update_data(ism=text.capitalize())
    await state.set_state(RegState.familiya)
    await message.answer(
        "2️⃣  Familiyańızdı kiritiń:\n"
        "<i>(Mısalı: Xojanov)</i>",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML",
    )


# ─── Step 2 — familiya ────────────────────────────────────────────────────────

@router.message(RegState.familiya)
async def step_familiya(message: types.Message, state: FSMContext) -> None:
    text = (message.text or "").strip()

    if len(text) < 2 or not re.match(r"^[A-Za-zА-Яа-яЁёÓóÁáÉéÍíÚúÑñQqWw'\- ]+$", text, re.UNICODE):
        await message.answer(
            "❌ Familiyańızdı durıs kiritiń!\n"
            "<i>(Keminde 2 hárip, bir hárip bolıwı kerek)</i>",
            parse_mode="HTML",
        )
        return

    await state.update_data(familiya=text.capitalize())
    await state.set_state(RegState.til)
    await message.answer(
        "3️⃣  Imtixan tilin saylań 👇",
        reply_markup=language_keyboard(),
    )


# ─── Step 3 — til ─────────────────────────────────────────────────────────────

@router.message(RegState.til, F.text.in_(LANG_OPTIONS))
async def step_til_valid(message: types.Message, state: FSMContext) -> None:
    await state.update_data(til=message.text)
    await state.set_state(RegState.telefon)
    await message.answer(
        "4️⃣  Telefon nomeriňizdi jiberiň 📞\n\n"
        "Tómendegi <b>«Telefon nomerin jiberiw»</b> túymesin basıń\n"
        "<i>yamasa +998XXXXXXXXX formatında qol benen kiritiń</i>",
        reply_markup=phone_keyboard(),
        parse_mode="HTML",
    )


@router.message(RegState.til)
async def step_til_invalid(message: types.Message) -> None:
    await message.answer(
        "❌ Tómendegi túymelerden birini saylań!",
        reply_markup=language_keyboard(),
    )


# ─── Step 4 — telefon (contact button) ───────────────────────────────────────

@router.message(RegState.telefon, F.contact)
async def step_telefon_contact(message: types.Message, state: FSMContext) -> None:
    phone = message.contact.phone_number
    if not phone.startswith("+"):
        phone = "+" + phone
    await _finish(message, state, phone)


# ─── Step 4 — telefon (manual text) ──────────────────────────────────────────

@router.message(RegState.telefon)
async def step_telefon_text(message: types.Message, state: FSMContext) -> None:
    raw = (message.text or "").strip()
    phone = normalize_phone(raw)

    if not phone:
        await message.answer(
            "❌ Telefon nomeri nadurıs!\n"
            "<i>Mısalı: +998901234567</i>",
            reply_markup=phone_keyboard(),
            parse_mode="HTML",
        )
        return

    await _finish(message, state, phone)


# ─── Finish ───────────────────────────────────────────────────────────────────

async def _finish(message: types.Message, state: FSMContext, phone: str) -> None:
    data = await state.get_data()
    ism      = data["ism"]
    familiya = data["familiya"]
    til      = data["til"]

    success = await add_user(
        telegram_id=message.from_user.id,
        ism=ism,
        familiya=familiya,
        til=til,
        telefon=phone,
    )
    await state.clear()

    if not success:
        await message.answer(
            "⚠️ Siz burın registraciyadan ótkensiź!\n"
            "/start komandasın basıń.",
            reply_markup=main_menu_keyboard(),
        )
        return

    logger.info(
        f"Registered: {message.from_user.id} | {ism} {familiya} | {til} | {phone}"
    )

    await message.answer(
        "🎉 <b>Registraciya tastıyıqlanǵan!</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 Atı:       <b>{ism}</b>\n"
        f"👤 Familiyası: <b>{familiya}</b>\n"
        f"🌐 Til:       <b>{til}</b>\n"
        f"📞 Telefon:   <b>{phone}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "✅ Maǵlıwmatlarıńız saqlandı.\n"
        "Demo imtixan 2-iyun kúni 09:00de Mektebimizde bolıp ótedi.\n\n"
        "🌟 Áwmet yar bolsın!",
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML",
    )
