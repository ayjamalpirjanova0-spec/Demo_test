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
CANCEL_TEXT = "❌ Bekor qılıw"

# Xojeli tumanları
TUMANLAR = [
    "🏙️ Xojeli rayonı",
    "🏙️ Nókis qalası",
    "🏙️ Beruniy rayonı",
    "🏙️ Shımbay rayonı",
    "🏙️ Ellikqala rayonı",
    "🏙️ Kegeyli rayonı",
    "🏙️ Qanlıkól rayonı",
    "🏙️ Shomanay rayonı",
    "🏙️ Qońırat rayonı",
    "🏙️ Qaragalpaqstan Respublikası (basqa)",
]


class RegState(StatesGroup):
    ism      = State()
    familiya = State()
    tuman    = State()
    maktab   = State()
    til      = State()
    telefon  = State()


def normalize_phone(raw: str) -> str | None:
    cleaned = re.sub(r"[\s\-()]", "", raw)
    if not re.match(r"^\+?\d{9,15}$", cleaned):
        return None
    if not cleaned.startswith("+"):
        cleaned = "+" + cleaned
    return cleaned


def tuman_keyboard() -> types.ReplyKeyboardMarkup:
    builder_rows = []
    for t in TUMANLAR:
        builder_rows.append([types.KeyboardButton(text=t)])
    builder_rows.append([types.KeyboardButton(text=CANCEL_TEXT)])
    return types.ReplyKeyboardMarkup(
        keyboard=builder_rows,
        resize_keyboard=True,
    )


# ─── Cancel anytime ───────────────────────────────────────────────────────────

@router.message(StateFilter(RegState), F.text == CANCEL_TEXT)
async def cancel_registration(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "🚫 Registraciya bekor qılındı.\n\n"
        "Qaytadan baslaw ushın tómendegi túymeni basıń 👇",
        reply_markup=main_menu_keyboard(),
    )


# ─── Step 0 — trigger ─────────────────────────────────────────────────────────

@router.message(F.text == "📋 Registraciya")
async def start_registration(message: types.Message, state: FSMContext) -> None:
    user = await get_user(message.from_user.id)
    if user:
        # id, telegram_id, ism, familiya, tuman, maktab, til, telefon, sana
        await message.answer(
            "✅ <b>Siz burın registraciyadan ótkensiź!</b>\n\n"
            f"👤 Atı: <b>{user[2]}</b>\n"
            f"👤 Familiyası: <b>{user[3]}</b>\n"
            f"🏙️ Tuman: <b>{user[4]}</b>\n"
            f"🏫 Mektep: <b>{user[5]}</b>\n"
            f"🌐 Til: <b>{user[6]}</b>\n"
            f"📞 Telefon: <b>{user[7]}</b>\n\n"
            f"📅 Sana: <b>{user[8]}</b>",
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML",
        )
        return

    await state.set_state(RegState.ism)
    await message.answer(
        "📝 <b>Registraciya baslandı!</b>\n\n"
        "1️⃣  Atıńızdı kiriting:\n"
        "<i>(Mısalı: Alibek)</i>",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML",
    )


# ─── Step 1 — ism ─────────────────────────────────────────────────────────────

@router.message(RegState.ism)
async def step_ism(message: types.Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if len(text) < 2:
        await message.answer(
            "❌ Atıńızdı durıs kiriting!\n"
            "<i>(Keminde 2 háripler bolıwı kerek)</i>",
            parse_mode="HTML",
        )
        return
    await state.update_data(ism=text.capitalize())
    await state.set_state(RegState.familiya)
    await message.answer(
        "2️⃣  Familiyańızdı kiriting:\n"
        "<i>(Mısalı: Xojanov)</i>",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML",
    )


# ─── Step 2 — familiya ────────────────────────────────────────────────────────

@router.message(RegState.familiya)
async def step_familiya(message: types.Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if len(text) < 2:
        await message.answer(
            "❌ Familiyańızdı durıs kiriting!\n"
            "<i>(Keminde 2 háripler bolıwı kerek)</i>",
            parse_mode="HTML",
        )
        return
    await state.update_data(familiya=text.capitalize())
    await state.set_state(RegState.tuman)
    await message.answer(
        "3️⃣  Qaysi tumandasiź? Saylańız 👇",
        reply_markup=tuman_keyboard(),
    )


# ─── Step 3 — tuman ───────────────────────────────────────────────────────────

@router.message(RegState.tuman, F.text.in_(TUMANLAR))
async def step_tuman_valid(message: types.Message, state: FSMContext) -> None:
    await state.update_data(tuman=message.text)
    await state.set_state(RegState.maktab)
    await message.answer(
        "4️⃣  Qaysi mektepten kelesiź?\n\n"
        "Mektep nomerin yamasa atın kiriting:\n"
        "<i>(Mısalı: 5-mektep yoki Abu Ali ibn Sino mektebi)</i>",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML",
    )


@router.message(RegState.tuman)
async def step_tuman_invalid(message: types.Message) -> None:
    await message.answer(
        "❌ Tómendegi túymelerden birini saylańız!",
        reply_markup=tuman_keyboard(),
    )


# ─── Step 4 — maktab ──────────────────────────────────────────────────────────

@router.message(RegState.maktab)
async def step_maktab(message: types.Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if len(text) < 2:
        await message.answer(
            "❌ Mektep atın durıs kiriting!\n"
            "<i>(Keminde 2 háripler bolıwı kerek)</i>",
            parse_mode="HTML",
        )
        return
    await state.update_data(maktab=text)
    await state.set_state(RegState.til)
    await message.answer(
        "5️⃣  Imtixan tilini saylańız 👇",
        reply_markup=language_keyboard(),
    )


# ─── Step 5 — til ─────────────────────────────────────────────────────────────

@router.message(RegState.til, F.text.in_(LANG_OPTIONS))
async def step_til_valid(message: types.Message, state: FSMContext) -> None:
    await state.update_data(til=message.text)
    await state.set_state(RegState.telefon)
    await message.answer(
        "6️⃣  Telefon nomeriňizdi jiberiň 📞\n\n"
        "Tómendegi <b>«Telefon nomerin jiberiw»</b> túymesin basıń\n"
        "<i>yamasa +998XXXXXXXXX formatında qol benen kiriting</i>",
        reply_markup=phone_keyboard(),
        parse_mode="HTML",
    )


@router.message(RegState.til)
async def step_til_invalid(message: types.Message) -> None:
    await message.answer(
        "❌ Tómendegi túymelerden birini saylańız!",
        reply_markup=language_keyboard(),
    )


# ─── Step 6 — telefon (contact) ───────────────────────────────────────────────

@router.message(RegState.telefon, F.contact)
async def step_telefon_contact(message: types.Message, state: FSMContext) -> None:
    phone = message.contact.phone_number
    if not phone.startswith("+"):
        phone = "+" + phone
    await _finish(message, state, phone)


@router.message(RegState.telefon)
async def step_telefon_text(message: types.Message, state: FSMContext) -> None:
    raw = (message.text or "").strip()
    phone = normalize_phone(raw)
    if not phone:
        await message.answer(
            "❌ Telefon nomeri noto'g'ri!\n"
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
    tuman    = data["tuman"]
    maktab   = data["maktab"]
    til      = data["til"]

    success = await add_user(
        telegram_id=message.from_user.id,
        ism=ism,
        familiya=familiya,
        tuman=tuman,
        maktab=maktab,
        til=til,
        telefon=phone,
    )
    await state.clear()

    if not success:
        await message.answer(
            "⚠️ Siz burın registraciyadan ótkensiź!\n/start komandasın basıń.",
            reply_markup=main_menu_keyboard(),
        )
        return

    logger.info(f"Registered: {message.from_user.id} | {ism} {familiya} | {tuman} | {maktab} | {til} | {phone}")

    await message.answer(
        "🎉 <b>Registraciya wákillengen!</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 Atı:        <b>{ism}</b>\n"
        f"👤 Familiyası: <b>{familiya}</b>\n"
        f"🏙️ Tuman:     <b>{tuman}</b>\n"
        f"🏫 Mektep:    <b>{maktab}</b>\n"
        f"🌐 Til:        <b>{til}</b>\n"
        f"📞 Telefon:   <b>{phone}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"

        "✅ Maǵlıwmatlarıńız saqlandı.\n"
        "Demo imtixan 2-iyun kúni 09:00de Mektebimizde bolıp ótedi.\n\n"
        "🌟 Áwmet yar bolsın!",
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML",
    )
