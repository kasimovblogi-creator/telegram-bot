


import sqlite3
import time
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

import os

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

CHANNEL = "@saudiya_sari1"
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8479973325  # <-- o'zingni Telegram ID

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
check_cache = {}

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
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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

        conn.commit()

    # 👇 KNOPKALAR
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("📢 Kanalga azo bo‘lish", url=f"https://t.me/{CHANNEL[1:]}"),
        InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub")
    )

    await message.answer(
        "Assalamu alaykum!\n\n"
        "Siz mahsus link orqali yaqinlaringizni taklif qilib "
        "Saudiya universitetlariga bepul hujjat topshirish imkoniyatiga ega bo‘lasiz!\n\n"
        "❗ Konkursda qatnashish uchun kanalimizga azo bo‘ling",
        reply_markup=keyboard
    )
#======================obunani tekshirish============

@dp.callback_query_handler(lambda c: c.data == "check_sub")
async def check_subscription(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    member = await bot.get_chat_member(CHANNEL, user_id)

    if member.status in ["member", "administrator", "creator"]:
        # referral reward ishlaydi shu yerda
        cursor.execute("SELECT referrer_id FROM users WHERE user_id=?", (user_id,))
        ref = cursor.fetchone()

        if ref and ref[0]:
            referrer_id = ref[0]

            cursor.execute("""
                UPDATE users
                SET points = points + 5,
                    referrals = referrals + 1
                WHERE user_id=?
            """, (referrer_id,))
            conn.commit()

            # 📩 XABAR REFERRERGA
            try:
                await bot.send_message(
                    referrer_id,
                    "🎉 Tabriklaymiz! Sizning linkingiz orqali yangi foydalanuvchi qo‘shildi!\n+5 ball"
                )
            except:
                pass

        link = f"https://t.me/saudiyasari_bot?start={user_id}"

        await callback.message.answer(
            "🎉 Tabriklaymiz siz azo bo‘ldingiz!\n\n"
            "Endi ushbu link orqali atigi 10 ta odam taklif qiling va 50 ball bilan konkursda qatnashing!\n\n"
            f"🔗 Sizning linkingiz:\n{link}"
        )

    else:
        await callback.message.answer(
            "❌ Kechirasiz, siz kanalga azo bo‘lmadingiz. Iltimos azo bo‘ling!"
        )

    await callback.answer()

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

#=================chek sub================


@dp.callback_query_handler(lambda c: c.data == "check_sub")
async def check_subscription(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    now = time.time()

    # 🔥 CACHE (sekinlikni kamaytiradi)
    if user_id in check_cache and now - check_cache[user_id] < 10:
        return await callback.answer("⏳ Iltimos biroz kuting...", show_alert=True)

    check_cache[user_id] = now

    # 📡 Kanalni tekshirish
    member = await bot.get_chat_member(CHANNEL, user_id)

    if member.status in ["member", "administrator", "creator"]:

        # 🔥 referral olish
        cursor.execute("SELECT referrer_id FROM users WHERE user_id=?", (user_id,))
        ref = cursor.fetchone()

        if ref and ref[0]:
            referrer_id = ref[0]

            cursor.execute("""
                UPDATE users
                SET points = points + 5,
                    referrals = referrals + 1
                WHERE user_id=?
            """, (referrer_id,))
            conn.commit()

            # 📩 REFERRERGA XABAR
            try:
                cursor.execute("SELECT points FROM users WHERE user_id=?", (referrer_id,))
                points = cursor.fetchone()[0]

                await bot.send_message(
                    referrer_id,
                    f"🎉 Tabriklaymiz! Yangi odam qo‘shildi!\n"
                    f"+5 ball\n\n"
                    f"⭐ Jami ballingiz: {points}"
                )
            except:
                pass

        link = f"https://t.me/saudiyasari_bot?start={user_id}"

        await callback.message.answer(
            "🎉 Tabriklaymiz siz kanalga azo bo‘ldingiz!\n\n"
            "👥 Endi 10 ta odam taklif qiling va 50 ball bilan konkursda qatnashing!\n\n"
            f"🔗 Sizning referral linkingiz:\n{link}"
        )

    else:
        await callback.message.answer(
            "❌ Siz kanalga azo bo‘lmadingiz.\n"
            "Iltimos avval kanalga azo bo‘ling!"
        )

    await callback.answer()

# ================= ADMIN PANEL =================
@dp.message_handler(commands=['admin'])
async def admin(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("⛔ Ruxsat yo‘q")

    cursor.execute("SELECT COUNT(*) FROM users")
    total = cursor.fetchone()[0]

    await message.answer(f"🧑‍💼 Admin panel\n👥 Users: {total}")
    # ================= WINNERS =================
@dp.message_handler(commands=['winners'])
async def winners(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    cursor.execute("""
        SELECT user_id, referrals
        FROM users
        WHERE referrals >= 10
        ORDER BY referrals DESC
    """)
    data = cursor.fetchall()

    text = "🏆 10+ referral qilganlar:\n\n"

    for uid, ref in data:
        text += f"{uid} — {ref}\n"

    await message.answer(text)

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