import os
import json
import asyncio
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# ─── SOZLAMALAR ───────────────────────────────────────────
BOT_TOKEN  = os.getenv("BOT_TOKEN", "8882915414:AAFRzmTDFIvsl25iV00i4QEzpTaegQTyT7s")
WEBAPP_URL = "https://sardor00990.github.io/Habitracer"

bot    = Bot(token=BOT_TOKEN)
dp     = Dispatcher()
router = Router()
dp.include_router(router)

# Foydalanuvchilar ro'yxati (bot qayta ishga tushsa ham saqlansin)
USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(list(users), f)

users: set = load_users()


# ─── KLAVIATURA ───────────────────────────────────────────
def main_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="📓 Odatlarni kuzatish", web_app=WebAppInfo(url=WEBAPP_URL))
    kb.button(text="📊 Statistika", web_app=WebAppInfo(url=WEBAPP_URL + "?tab=stats"))
    kb.adjust(1)
    return kb.as_markup()


# ─── /start ───────────────────────────────────────────────
@router.message(CommandStart())
async def start(message: types.Message):
    users.add(message.from_user.id)
    save_users(users)

    name = message.from_user.first_name or "Do'st"
    await message.answer(
        f"Salom, <b>{name}</b>! 👋\n\n"
        f"<b>Odat Kuzatuvchi</b>ga xush kelibsiz! 🎯\n\n"
        f"Bu bot sizga:\n"
        f"✅ Odatlarni har kuni kuzatishga\n"
        f"🔥 Zanjirni uzmaslikka\n"
        f"📊 Haftalik natijalarni ko'rishga yordam beradi\n\n"
        f"<b>Buyruqlar:</b>\n"
        f"/start — bosh menyu\n"
        f"/stats — bugungi natija\n"
        f"/help — yordam\n\n"
        f"⏰ Har kuni <b>21:00</b> da eslatma keladi\n"
        f"📊 Har <b>dushanba</b> haftalik hisobot keladi",
        parse_mode="HTML",
        reply_markup=main_kb()
    )


# ─── /help ────────────────────────────────────────────────
@router.message(Command("help"))
async def help_cmd(message: types.Message):
    await message.answer(
        "📖 <b>Qanday foydalanish:</b>\n\n"
        "1️⃣ <b>Odatlarni sozlash</b> — ilovada odatlarni qo'shing\n"
        "2️⃣ <b>Har kuni belgilang</b> — bajargan odatlaringizni ✅ qiling\n"
        "3️⃣ <b>Zanjirni ushlang</b> — ketma-ket kunlar streak hosil qiladi\n"
        "4️⃣ <b>Tahlilni ko'ring</b> — grafik va statistika ilovada\n\n"
        "⏰ <b>Eslatmalar:</b>\n"
        "• Har kuni 21:00 — kechki eslatma\n"
        "• Har dushanba 09:00 — haftalik hisobot\n\n"
        "💾 Ma'lumotlar Telegram CloudStorage'da saqlanadi",
        parse_mode="HTML",
        reply_markup=main_kb()
    )


# ─── /stats ───────────────────────────────────────────────
@router.message(Command("stats"))
async def stats_cmd(message: types.Message):
    await message.answer(
        "📊 <b>Statistikangiz:</b>\n\n"
        "Batafsil tahlil ilovada mavjud 👇",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text="📊 Tahlilni ko'rish",
                web_app=WebAppInfo(url=WEBAPP_URL + "?tab=stats")
            )
        ]])
    )


# ─── WEBAPP DAN KELGAN MA'LUMOT ───────────────────────────
@router.message(F.web_app_data)
async def handle_webapp_data(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)

        if data.get("action") == "summary":
            day     = data.get("daysPassed", 0) + 1
            done    = data.get("totalDone", 0)
            total   = data.get("totalPossible", 0)
            pct     = data.get("percentage", 0)
            streak  = data.get("bestStreak", 0)

            # Ball hisoblash
            if pct >= 80:
                grade = "🏆 Ajoyib!"
                msg   = "Siz haqiqatan ham intizomli odamsiz!"
            elif pct >= 60:
                grade = "👍 Yaxshi!"
                msg   = "Davom eting, natija ko'rinyapti!"
            elif pct >= 40:
                grade = "⚡ O'rta"
                msg   = "Bir oz ko'proq e'tibor bering."
            else:
                grade = "💡 Yaxshilang"
                msg   = "Har kun kichik qadam katta natija beradi."

            await message.answer(
                f"📊 <b>Natijangiz</b>\n\n"
                f"📅 {day}-kun\n"
                f"✅ Bajarildi: <b>{done}/{total}</b>\n"
                f"📈 Muvaffaqiyat: <b>{pct}%</b>\n"
                f"🔥 Eng uzun streak: <b>{streak} kun</b>\n\n"
                f"<b>{grade}</b> — {msg}",
                parse_mode="HTML"
            )

    except Exception as e:
        print(f"WebApp data error: {e}")


# ─── ESLATMALAR ───────────────────────────────────────────
async def evening_reminder():
    """Har kuni 21:00 — kechki eslatma"""
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="✅ Odatlarni belgilash",
            web_app=WebAppInfo(url=WEBAPP_URL + "?tab=tracker")
        )
    ]])

    msgs = [
        "🌙 Kechqurun keldi! Bugungi odatlarni belgiladingizmi?",
        "⭐ Yaxshi kun bo'ldimi? Odatlarni belgilashni unutmang!",
        "🔥 Streakingizni saqlab qoling — bugun ham belgilang!",
        "🎯 Har kun bir qadam — odatlarni belgilash vaqti!",
        "💪 Kichik harakat, katta o'zgarish. Bugun ham bajardingizmi?",
    ]

    import random
    text = random.choice(msgs)

    for user_id in list(users):
        try:
            await bot.send_message(user_id, text, reply_markup=kb)
        except Exception as e:
            print(f"Reminder error for {user_id}: {e}")
            # Foydalanuvchi botni bloklagan bo'lishi mumkin
            if "blocked" in str(e).lower() or "deactivated" in str(e).lower():
                users.discard(user_id)
                save_users(users)


async def weekly_report():
    """Har dushanba 09:00 — haftalik hisobot"""
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="📊 To'liq tahlilni ko'rish",
            web_app=WebAppInfo(url=WEBAPP_URL + "?tab=stats")
        )
    ]])

    now = datetime.now()
    week_num = now.isocalendar()[1]

    for user_id in list(users):
        try:
            await bot.send_message(
                user_id,
                f"📊 <b>{week_num}-hafta tugadi!</b>\n\n"
                f"Haftalik natijangizni ko'rish vaqti.\n\n"
                f"✅ Bajargan odatlar soni oshyaptimi?\n"
                f"🔥 Streakingiz qanday?\n"
                f"📈 Qaysi odat eng yaxshi?\n\n"
                f"<i>Tahlilni ilovada ko'ring 👇</i>",
                parse_mode="HTML",
                reply_markup=kb
            )
        except Exception as e:
            print(f"Weekly report error for {user_id}: {e}")
            if "blocked" in str(e).lower() or "deactivated" in str(e).lower():
                users.discard(user_id)
                save_users(users)


# ─── MAIN ─────────────────────────────────────────────────
async def main():
    # Scheduler sozlash
    scheduler = AsyncIOScheduler(timezone="Asia/Tashkent")

    # Har kuni 21:00 — kechki eslatma
    scheduler.add_job(
        evening_reminder,
        CronTrigger(hour=21, minute=0),
        id="evening"
    )

    # Har dushanba 09:00 — haftalik hisobot
    scheduler.add_job(
        weekly_report,
        CronTrigger(day_of_week="mon", hour=9, minute=0),
        id="weekly"
    )

    scheduler.start()
    print("✅ Scheduler ishga tushdi!")
    print("⏰ Eslatma: har kuni 21:00")
    print("📊 Haftalik: har dushanba 09:00")

    print("🤖 Bot ishga tushdi!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
