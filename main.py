import os
import json
import asyncio
import random
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
WEBAPP_URL = "https://sardor00990.github.io/Habitracer"
USERS_FILE = "users.json"

bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher(bot)

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE) as f:
            return set(json.load(f))
    return set()

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(list(users), f)

users = load_users()

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    users.add(message.from_user.id)
    save_users(users)
    name = message.from_user.first_name or "Do'st"
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("📓 Odatlarni kuzatish", web_app=types.WebAppInfo(url=WEBAPP_URL)))
    kb.add(types.InlineKeyboardButton("📊 Statistika", web_app=types.WebAppInfo(url=WEBAPP_URL + "?tab=stats")))
    await message.answer(
        f"Salom, <b>{name}</b>! 👋\n\n"
        f"<b>Odat Kuzatuvchi</b>ga xush kelibsiz! 🎯\n\n"
        f"✅ Odatlarni har kuni kuzatish\n"
        f"🔥 Zanjirni uzmaslik\n"
        f"📊 Haftalik natijalarni ko'rish\n\n"
        f"⏰ Har kuni <b>21:00</b> da eslatma keladi\n"
        f"📊 Har <b>dushanba</b> haftalik hisobot keladi",
        parse_mode="HTML", reply_markup=kb
    )

@dp.message_handler(commands=["help"])
async def help_cmd(message: types.Message):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("📓 Ilovani ochish", web_app=types.WebAppInfo(url=WEBAPP_URL)))
    await message.answer(
        "📖 <b>Qanday foydalanish:</b>\n\n"
        "1️⃣ Ilovani oching\n"
        "2️⃣ Odatlarni qo'shing\n"
        "3️⃣ Har kuni ✅ belgilang\n"
        "4️⃣ Tahlilni ko'ring 📊\n\n"
        "⏰ Har kuni 21:00 eslatma\n"
        "📊 Har dushanba hisobot",
        parse_mode="HTML", reply_markup=kb
    )

@dp.message_handler(commands=["stats"])
async def stats_cmd(message: types.Message):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("📊 Tahlilni ko'rish", web_app=types.WebAppInfo(url=WEBAPP_URL + "?tab=stats")))
    await message.answer("📊 Statistikangiz:", parse_mode="HTML", reply_markup=kb)

@dp.message_handler(content_types=types.ContentType.WEB_APP_DATA)
async def handle_webapp(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)
        if data.get("action") == "summary":
            day    = data.get("daysPassed", 0) + 1
            done   = data.get("totalDone", 0)
            total  = data.get("totalPossible", 0)
            pct    = data.get("percentage", 0)
            streak = data.get("bestStreak", 0)
            if pct >= 80: grade, msg = "🏆 Ajoyib!", "Siz haqiqatan ham intizomli odamsiz!"
            elif pct >= 60: grade, msg = "👍 Yaxshi!", "Davom eting!"
            elif pct >= 40: grade, msg = "⚡ O'rta", "Bir oz ko'proq e'tibor bering."
            else: grade, msg = "💡 Yaxshilang", "Har kun kichik qadam katta natija beradi."
            await message.answer(
                f"📊 <b>Natijangiz</b>\n\n"
                f"📅 {day}-kun\n"
                f"✅ Bajarildi: <b>{done}/{total}</b>\n"
                f"📈 Muvaffaqiyat: <b>{pct}%</b>\n"
                f"🔥 Streak: <b>{streak} kun</b>\n\n"
                f"<b>{grade}</b> — {msg}",
                parse_mode="HTML"
            )
    except Exception as e:
        print(f"WebApp error: {e}")

async def evening_reminder():
    msgs = [
        "🌙 Bugungi odatlarni belgiladingizmi?",
        "⭐ Streakingizni saqlab qoling!",
        "🔥 Har kun bir qadam — odatlarni belgilang!",
        "💪 Kichik harakat, katta o'zgarish!",
    ]
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("✅ Belgilash", web_app=types.WebAppInfo(url=WEBAPP_URL + "?tab=tracker")))
    for user_id in list(users):
        try:
            await bot.send_message(user_id, random.choice(msgs), reply_markup=kb)
        except Exception as e:
            print(f"Reminder error {user_id}: {e}")

async def weekly_report():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("📊 Tahlilni ko'rish", web_app=types.WebAppInfo(url=WEBAPP_URL + "?tab=stats")))
    week = datetime.now().isocalendar()[1]
    for user_id in list(users):
        try:
            await bot.send_message(
                user_id,
                f"📊 <b>{week}-hafta tugadi!</b>\n\n"
                f"Haftalik natijangizni ko'ring 👇",
                parse_mode="HTML", reply_markup=kb
            )
        except Exception as e:
            print(f"Weekly error {user_id}: {e}")

async def on_startup(dp):
    scheduler = AsyncIOScheduler(timezone="Asia/Tashkent")
    scheduler.add_job(evening_reminder, CronTrigger(hour=21, minute=0))
    scheduler.add_job(weekly_report, CronTrigger(day_of_week="mon", hour=9, minute=0))
    scheduler.start()
    print("✅ Bot ishga tushdi!")

if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
