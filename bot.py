import sqlite3
import time
import os
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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
    user_id INTEGER PRIMARY KEY
)
""")
conn.commit()

def add_user(user_id):
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

def get_user_count():
    cursor.execute("SELECT COUNT(*) FROM users")
    return cursor.fetchone()[0]

# ================= KEYBOARD =================
def sub_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton(
            "📢 Kanalga azo bo‘lish",
            url=f"https://t.me/{CHANNEL[1:]}"
        ),
        InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub")
    )
    return kb

def channel_button():
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton(
            "📢 Kanalga o'tish",
            url=f"https://t.me/{CHANNEL[1:]}"
        )
    )
    return kb

# ================= START =================
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_user.id

    add_user(user_id)
    count = get_user_count()

    await bot.send_message(
        ADMIN_ID,
        f"🆕 Yangi user!\nID: {user_id}\n👥 Jami: {count}"
    )

    await message.answer(
        "Assalamu alaykum qo'llanmani qo'lga kiritish uchun kanalga azo bo'ling",
        reply_markup=sub_keyboard()
    )

# ================= HAMMA USERNI SAQLASH =================
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
@dp.callback_query_handler(lambda c: c.data == "check_sub")
async def check_sub(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    add_user(user_id)

    try:
        member = await bot.get_chat_member(CHANNEL, user_id)

        if member.status in ["member", "administrator", "creator"]:
            await callback.message.answer(
                "kechirasiz qo'llanma tayyor emasligi sabab biroz kutib turishingizga to'g'ri keladi kanalimizni kuzating albatta qo'llanmani beramiz",
                reply_markup=channel_button()
            )
        else:
            await callback.message.answer("❌ Avval kanalga azo bo‘ling!")

    except:
        await callback.message.answer("⚠️ Kanalni tekshirib bo‘lmadi")

    await callback.answer()

# ================= RUN =================
if __name__ == "__main__":
    print("BOT START 🚀")
    executor.start_polling(dp, skip_updates=True)