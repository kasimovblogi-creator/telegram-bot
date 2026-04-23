import sqlite3
import time
import os
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ================= CONFIG =================
CHANNEL = "@saudiya_sari1"
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8479973325

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# ================= DATABASE =================
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()


def add_user(user_id):
    try:
        cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
    except Exception as e:
        logging.error(f"DB error: {e}")


def get_user_count():
    cursor.execute("SELECT COUNT(*) FROM users")
    return cursor.fetchone()[0]


# ================= ANTI SPAM =================
last_message_time = {}

def is_spam(user_id):
    now = time.time()
    if user_id in last_message_time:
        if now - last_message_time[user_id] < 1:
            return True
    last_message_time[user_id] = now
    return False


# ================= KEYBOARD =================
def subscribe_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(
            "📢 Kanalga azo bo‘lish",
            url=f"https://t.me/{CHANNEL[1:]}"
        ),
        InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub")
    )
    return keyboard


# ================= START =================
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_user.id

    if is_spam(user_id):
        return

    add_user(user_id)
    count = get_user_count()

    await bot.send_message(
        ADMIN_ID,
        f"🆕 Yangi user: {user_id}\n👥 Jami: {count}"
    )

    await message.answer(
        "📢 Assalomu alaykum!\n\n"
        "Qo‘llanma olish uchun kanalga obuna bo‘ling!",
        reply_markup=subscribe_keyboard()
    )


# ================= AUTO SAVE USERS =================
@dp.message_handler()
async def all_messages(message: types.Message):
    add_user(message.from_user.id)


# ================= STATS =================
@dp.message_handler(commands=['stats'])
async def stats(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    count = get_user_count()
    await message.answer(f"👥 Foydalanuvchilar soni: {count}")


# ================= CHECK SUB =================
check_cache = {}

@dp.callback_query_handler(lambda c: c.data == "check_sub")
async def check_subscription(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    add_user(user_id)

    now = time.time()
    if user_id in check_cache and now - check_cache[user_id] < 5:
        return await callback.answer("⏳ Kuting...", show_alert=True)

    check_cache[user_id] = now

    try:
        member = await bot.get_chat_member(CHANNEL, user_id)

        if member.status in ["member", "administrator", "creator"]:
            await callback.message.answer("✅ Obuna tasdiqlandi!")
        else:
            await callback.message.answer(
                "❌ Avval kanalga azo bo‘ling!",
                reply_markup=subscribe_keyboard()
            )
    except Exception as e:
        logging.error(f"Check sub error: {e}")
        await callback.message.answer("⚠️ Xatolik yuz berdi")

    await callback.answer()


# ================= BROADCAST =================
@dp.message_handler(commands=['send'])
async def broadcast(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    text = message.get_args()
    if not text:
        return await message.answer("❗ Matn yozing: /send salom")

    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()

    success = 0
    fail = 0

    for user in users:
        try:
            await bot.send_message(user[0], text)
            success += 1
            await asyncio.sleep(0.05)
        except:
            fail += 1

    await message.answer(f"✅ Yuborildi: {success}\n❌ Xato: {fail}")


# ================= RUN =================
if __name__ == "__main__":
    print("BOT START 🚀")
    executor.start_polling(dp, skip_updates=True)