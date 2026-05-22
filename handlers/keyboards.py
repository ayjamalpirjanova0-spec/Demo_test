"""Umumiy klaviaturalar."""
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Asosiy menyu tugmalari."""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="📋 Registraciya"),
        KeyboardButton(text="ℹ️ Maǵlıwmat"),
    )
    return builder.as_markup(resize_keyboard=True)


def language_keyboard() -> ReplyKeyboardMarkup:
    """Til tanlash klaviaturasi."""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="🇺🇿 Ózbek tili"),
        KeyboardButton(text="📖 Qaraqalpaq tili"),
    )
    builder.row(KeyboardButton(text="❌ Bekor qılıw"))
    return builder.as_markup(resize_keyboard=True)


def phone_keyboard() -> ReplyKeyboardMarkup:
    """Telefon yuborish klaviaturasi."""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(
            text="📞 Telefon nomerin jiberiw",
            request_contact=True,
        )
    )
    builder.row(KeyboardButton(text="❌ Bekor qılıw"))
    return builder.as_markup(resize_keyboard=True)


def cancel_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="❌ Bekor qılıw"))
    return builder.as_markup(resize_keyboard=True)


def admin_keyboard() -> InlineKeyboardMarkup:
    """Admin panel inline tugmalari."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📋 Ro'yxat (20 ta)", callback_data="admin_list")
    )
    builder.row(
        InlineKeyboardButton(text="📄 CSV export", callback_data="admin_csv"),
        InlineKeyboardButton(text="📊 Excel export", callback_data="admin_excel"),
    )
    builder.row(
        InlineKeyboardButton(text="🔄 Yangilash", callback_data="admin_refresh")
    )
    return builder.as_markup()
