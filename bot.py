import sqlite3
import time
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

import os

TOKEN = os.getenv("8676426048:AAGc4WHnfpavDfUaG-LnD7rs34ZyLEEDCl4")
ADMIN_ID = 8479973325  # <-- o'zingni Telegram ID

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

# ================= DATABASE =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    referrer_id INTEGER,
    points INTEGER DEFAULT 0,
    referrals INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    last_bonus REAL DEFAULT 0
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
    user_id = message.from_user.id
    args = message.get_args()

    if is_spam(user_id):
        return

    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if not user:
        referrer_id = int(args) if args.isdigit() else None

        if referrer_id == user_id:
            referrer_id = None

        cursor.execute("""
            INSERT INTO users (user_id, referrer_id, points, referrals, clicks, last_bonus)
            VALUES (?, ?, 0, 0, 0, 0)
        """, (user_id, referrer_id))

        # referral reward
        if referrer_id:
            cursor.execute("""
                UPDATE users
                SET points = points + 5,
                    referrals = referrals + 1,
                    clicks = clicks + 1
                WHERE user_id=?
            """, (referrer_id,))

        conn.commit()

    link = f"https://t.me/saudiyasari_bot?start={user_id}"

    await message.answer(
        "👋 Xush kelibsiz! ushbu link orqali do'stlaringizni taklif qiling va saudiya univerlariga bepul hujjat topshiring\n\n"
        f"🔗 Referral link:\n{link}"
    )


# ================= STATS =================
@dp.message_handler(commands=['stats'])
async def stats(message: types.Message):
    user_id = message.from_user.id

    cursor.execute("""
        SELECT points, referrals, clicks
        FROM users WHERE user_id=?
    """, (user_id,))
    data = cursor.fetchone()

    if not data:
        return await message.answer("Avval /start bosing")

    points, referrals, clicks = data

    await message.answer(
        f"⭐ Points: {points}\n"
        f"👥 Referrals: {referrals}\n"
        f"👆 Clicks: {clicks}"
    )


# ================= TOP =================
@dp.message_handler(commands=['top'])
async def top(message: types.Message):
    cursor.execute("""
        SELECT user_id, referrals
        FROM users
        ORDER BY referrals DESC
        LIMIT 10
    """)
    data = cursor.fetchall()

    text = "🏆 TOP REFERRAL:\n\n"

    for i, (uid, ref) in enumerate(data, 1):
        text += f"{i}. {uid} — {ref}\n"

    await message.answer(text)


# ================= DAILY BONUS =================
@dp.message_handler(commands=['bonus'])
async def bonus(message: types.Message):
    user_id = message.from_user.id
    now = time.time()

    cursor.execute("SELECT last_bonus FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()

    if not row:
        return await message.answer("Avval /start bosing")

    last_bonus = row[0]

    if now - last_bonus < 86400:
        return await message.answer("⏳ Bonus allaqachon olingan (24h)")

    cursor.execute("""
        UPDATE users
        SET points = points + 10,
            last_bonus = ?
        WHERE user_id=?
    """, (now, user_id))

    conn.commit()

    await message.answer("🎁 Siz 10 ball bonus oldingiz!")


# ================= ADMIN PANEL =================
@dp.message_handler(commands=['admin'])
async def admin(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("⛔ Ruxsat yo‘q")

    cursor.execute("SELECT COUNT(*) FROM users")
    total = cursor.fetchone()[0]

    await message.answer(f"🧑‍💼 Admin panel\n👥 Users: {total}")


# ================= BROADCAST =================
@dp.message_handler(commands=['broadcast'])
async def broadcast(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    text = message.get_args()

    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()

    for u in users:
        try:
            await bot.send_message(u[0], f"📢 {text}")
        except:
            pass

    await message.answer("Yuborildi!")


# ================= RUN =================
if __name__ == "__main__":
    print("BOT START BO‘LDI 🚀")
    executor.start_polling(dp)