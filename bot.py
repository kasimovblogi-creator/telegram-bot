import sqlite3
import time
import os

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

CHANNEL = "@saudiya_sari1"
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8479973325  # <-- o'zingni ID yoz

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

check_cache = {}

# ================= DATABASE =================
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    clicks INTEGER DEFAULT 0
)
""")
conn.commit()

def add_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()

def get_user_count():
    cursor.execute("SELECT COUNT(*) FROM users")
    return cursor.fetchone()[0]

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
    user_id = message.from_user.id

    if is_spam(user_id):
        return

    add_user(user_id)
    count = get_user_count()

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(
            "📢 Kanalga azo bo‘lish",
            url=f"https://t.me/{CHANNEL[1:]}"
        ),
        InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub")
    )

    await bot.send_message(
        ADMIN_ID,
        f"🆕 Yangi user!\nID: {user_id}\n👥 Jami: {count}"
    )

    await message.answer(
        "📢 Assalomu alaykum!\n\n"
        "📚 Qo‘llanma olish uchun kanalga obuna bo‘ling!",
        reply_markup=keyboard
    )

# ================= STATS =================
@dp.message_handler(commands=['stats'])
async def stats(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    count = get_user_count()
    await message.answer(f"👥 Foydalanuvchilar soni: {count}")

# ================= CHECK SUB =================
@dp.callback_query_handler(lambda c: c.data == "check_sub")
async def check_subscription(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    now = time.time()

    if user_id in check_cache and now - check_cache[user_id] < 10:
        return await callback.answer("⏳ Kuting...", show_alert=True)

    check_cache[user_id] = now

    member = await bot.get_chat_member(CHANNEL, user_id)

    if member.status in ["member", "administrator", "creator"]:
        await callback.message.answer("✅ Obuna tasdiqlandi!")
    else:
        await callback.message.answer("❌ Avval kanalga azo bo‘ling!")

    await callback.answer()

# ================= RUN =================
if __name__ == "__main__":
    print("BOT START 🚀")
    executor.start_polling(dp)