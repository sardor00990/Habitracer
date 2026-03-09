import os
import asyncio
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ✏️ BU YERGA O'ZINGIZNING MA'LUMOTLARINGIZNI YOZING
BOT_TOKEN  = "8710371126:AAHTP7_cyHpqzJksL8QRRN0BCm7hm51JX_Y"   # ← tokeningiz
WEBAPP_URL = "https://sardor00990.github.io/Habitracer"           # ← sizning URL

bot    = Bot(token=BOT_TOKEN)
dp     = Dispatcher()
router = Router()
dp.include_router(router)

# ─── /start ───────────────────────────────────────────
@router.message(CommandStart())
async def start(message: types.Message):
    name = message.from_user.first_name or "Do'st"

    kb = InlineKeyboardBuilder()
    kb.button(
        text="📓 Odatlarni boshlash",
        web_app=WebAppInfo(url=WEBAPP_URL)
    )
    kb.adjust(1)

    await message.answer(
        f"Salom, <b>{name}</b>! 👋\n\n"
        f"<b>30 Kunlik Odat Kuzatuvchi</b>ga xush kelibsiz! 🎯\n\n"
        f"Quyidagi tugmani bosib odatlaringizni kuzatishni boshlang 👇",
        parse_mode="HTML",
        reply_markup=kb.as_markup()
    )

# ─── /help ────────────────────────────────────────────
@router.message(Command("help"))
async def help_cmd(message: types.Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="📓 Ilovani ochish", web_app=WebAppInfo(url=WEBAPP_URL))
    kb.adjust(1)

    await message.answer(
        "📖 <b>Qanday foydalanish:</b>\n\n"
        "1️⃣ Ilovani oching\n"
        "2️⃣ Odatlarni qo'shing\n"
        "3️⃣ Har kuni ✅ belgilang\n"
        "4️⃣ Grafikda natijangizni ko'ring 📊\n\n"
        "💾 Ma'lumotlar Telegram'da saqlanadi",
        parse_mode="HTML",
        reply_markup=kb.as_markup()
    )

# ─── MAIN ─────────────────────────────────────────────
async def main():
    print("🤖 Bot ishga tushdi!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
