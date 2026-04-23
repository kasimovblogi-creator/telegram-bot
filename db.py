import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

API_TOKEN = "8676426048:AAGc4WHnfpavDfUaG-LnD7rs34ZyLEEDCl4"
ADMIN_ID = 8479973325  # <-- o'zingizni Telegram ID

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# ---------------- DATABASE ----------------

def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY
    )
    """)

    conn.commit()
    conn.close()

def add_user(user_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR IGNORE INTO users (user_id)
    VALUES (?)
    """, (user_id,))

    conn.commit()
    conn.close()

def get_user_count():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]

    conn.close()
    return count

# ---------------- BOT ----------------

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_user.id

    add_user(user_id)

    count = get_user_count()
    conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM users")
print(cursor.fetchall())

conn.close()

    # ❌ userga hech narsa yuborilmaydi

    # ✅ faqat admin biladi
    await bot.send_message(
        ADMIN_ID,
        f"🆕 Yangi user kirdi!\n\n"
        f"👤 ID: {user_id}\n"
        f"👥 Jami userlar: {count} ta"
    )

# ---------------- START ----------------

if __name__ == '__main__':
    init_db()
    executor.start_polling(dp, skip_updates=True)