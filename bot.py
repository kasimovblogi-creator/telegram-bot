import sqlite3
import time
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import os
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

CHANNEL = "@saudiya_sari1"
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

check_cache = {}

conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

# ================= DATABASE =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    clicks INTEGER DEFAULT 0
)
""")
conn.commit()

# ================= ANTI SPAM =================
last_message_time = {}

def is_spam(user_id):
    now = time.time()
    if user_id in last_message_time:
        if now - last_message_time[user_id] < 1.5:
            return True
    last_message_time[user_id] = now
    return False

# ================= START =================
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
# ================= STATS (ADMIN ONLY) =================
@dp.message_handler(commands=['stats'])
async def stats(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]

    await message.answer(f"👥 Foydalanuvchilar soni: {count}")
    user_id = message.from_user.id

    if is_spam(user_id):
        return

    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if not user:
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(
            "📢 Kanalga azo bo‘lish",
            url=f"https://t.me/{CHANNEL[1:]}"
        ),
        InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub")
    )

    await message.answer(
        "📢 Assalomu alaykum!\n\n"
        "📚 Qo‘llanmani qo‘lga kiritish uchun kanalimizga obuna bo‘ling!",
        reply_markup=keyboard
    )

# ================= CHECK SUB =================
@dp.callback_query_handler(lambda c: c.data == "check_sub")
async def check_subscription(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    now = time.time()

    if user_id in check_cache and now - check_cache[user_id] < 10:
        return await callback.answer("⏳ Iltimos biroz kuting...", show_alert=True)

    check_cache[user_id] = now

    member = await bot.get_chat_member(CHANNEL, user_id)

    if member.status in ["member", "administrator", "creator"]:
        await callback.message.answer(
            "📌 Qabul hali ochilmaganligi sababli…\n"
            "⏳ Qo‘llanmani biroz kutishingizni so‘rab qolamiz.\n"
            "🚀 Qabul ochilishi bilan siz birinchilardan bo‘lib olasiz.\n"
            "👀 Bizni kuzatib boring!\n"
            "📚 Tez orada qo‘llanma taqdim qilinadi."
        )
    else:
        await callback.message.answer("❌ Iltimos avval kanalga azo bo‘ling!")

    await callback.answer()

# ================= RUN =================
if __name__ == "__main__":
    print("BOT START 🚀")
    executor.start_polling(dp)