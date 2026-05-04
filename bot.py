import os
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from db import init_db, add_user, get_user_count

# ================= CONFIG =================
CHANNEL = "@saudiya_sari1"
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8479973325

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# ================= DATABASE INIT =================
init_db()

# ================= USERS FILE =================
USERS_FILE = "users.txt"


def save_user(user_id):
    """Foydalanuvchini users.txt ga dublikatlarsiz saqlaydi"""
    uid = str(user_id)

    try:
        if not os.path.exists(USERS_FILE):
            with open(USERS_FILE, "w") as f:
                pass

        with open(USERS_FILE, "r") as f:
            users = f.read().splitlines()

        if uid not in users:
            with open(USERS_FILE, "a") as f:
                f.write(uid + "\n")

    except Exception as e:
        print("SAVE USER ERROR:", e)


def get_users():
    """users.txt dan userlarni oladi"""
    try:
        with open(USERS_FILE, "r") as f:
            return list(set(f.read().splitlines()))
    except:
        return []


# ================= KEYBOARD =================
def sub_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton(
            "📢 Kanalga a'zo bo‘lish",
            url=f"https://t.me/{CHANNEL[1:]}"
        ),
        InlineKeyboardButton(
            "✅ Tekshirish",
            callback_data="check_sub"
        )
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
    save_user(user_id)

    count = get_user_count()

    try:
        await bot.send_message(
            ADMIN_ID,
            f"🆕 Yangi user!\nID: {user_id}\n👥 Jami baza: {count}"
        )
    except:
        pass

    await message.answer(
        "Assalamu alaykum.\nQo'llanmani olish uchun kanalga a'zo bo‘ling 👇",
        reply_markup=sub_keyboard()
    )


# ================= MY ID =================
@dp.message_handler(commands=['myid'])
async def myid(message: types.Message):
    await message.reply(str(message.from_user.id))


# ================= STATS =================
@dp.message_handler(commands=['stats'])
async def stats(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    db_count = get_user_count()
    file_count = len(get_users())

    await message.answer(
        f"📊 Statistika\n\n"
        f"👥 Database: {db_count}\n"
        f"📄 users.txt: {file_count}"
    )


# ================= REKLAMA =================
@dp.message_handler(commands=['reklama'])
async def reklama(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.reply("❌ Siz admin emassiz")

    text = message.get_args()

    if not text:
        return await message.reply(
            "Matn kiriting:\n/reklama Assalomu alaykum hammaga"
        )

    users = get_users()

    if not users:
        return await message.reply("❌ Userlar topilmadi")

    sent = 0
    blocked = 0
    failed = 0

    await message.reply(f"📤 Reklama boshlandi...\n👥 Userlar: {len(users)}")

    for user in users:
        try:
            uid = int(user.strip())
            await bot.send_message(uid, text)
            sent += 1

        except Exception as e:
            err = str(e).lower()

            if "blocked" in err or "forbidden" in err:
                blocked += 1
            else:
                failed += 1

    await message.reply(
        f"✅ Reklama tugadi\n\n"
        f"📨 Yuborildi: {sent}\n"
        f"🚫 Block qilgan: {blocked}\n"
        f"❌ Xato: {failed}"
    )


# ================= CHECK SUB =================
@dp.callback_query_handler(lambda c: c.data == "check_sub")
async def check_sub(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    add_user(user_id)
    save_user(user_id)

    try:
        member = await bot.get_chat_member(CHANNEL, user_id)

        if member.status in ["member", "administrator", "creator"]:
            await callback.message.answer(
                "📘 Qo'llanma tayyor:\n👉 https://youtu.be/RKblPCGf0TQ",
                reply_markup=channel_button()
            )
        else:
            await callback.message.answer(
                "❌ Avval kanalga a'zo bo‘ling"
            )

    except:
        await callback.message.answer(
            "⚠️ Kanalni tekshirib bo‘lmadi"
        )

    await callback.answer()


# ================= RUN =================
if __name__ == "__main__":
    print("BOT START 🚀")
    executor.start_polling(dp, skip_updates=True)