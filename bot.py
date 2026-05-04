import os
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from db import init_db, add_user, get_user_count

CHANNEL = "@saudiya_sari1"
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8479973325

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# ================= DATABASE INIT =================
init_db()

# ================= USERS SAVE FIX =================
def save_user(user_id):
    try:
        with open("users.txt", "a") as f:
            f.write(str(user_id) + "\n")
    except:
        pass

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
    save_user(user_id)  # 🔥 FIX: users.txt ga yozadi

    count = get_user_count()

    await bot.send_message(
        ADMIN_ID,
        f"🆕 Yangi user!\nID: {user_id}\n👥 Jami: {count}"
    )

    await message.answer(
        "Assalamu alaykum, qo'llanmani olish uchun kanalga azo bo‘ling",
        reply_markup=sub_keyboard()
    )

# ================= MYID =================
@dp.message_handler(commands=['myid'])
async def myid(message: types.Message):
    await message.reply(str(message.from_user.id))

# ================= REKLAMA =================
@dp.message_handler(commands=['reklama'])
async def reklama(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.reply("Siz admin emassiz")

    text = message.get_args()

    if not text:
        return await message.reply("Matn yozing:\n/reklama Salom hammaga")

    try:
        users = open("users.txt", "r").readlines()
    except:
        return await message.reply("users.txt topilmadi")

    sent = 0

    for user in users:
        try:
            await bot.send_message(user.strip(), text)
            sent += 1
        except:
            pass

    await message.reply(f"Reklama yuborildi ✅ {sent} ta userga")

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
    save_user(user_id)  # 🔥 FIX

    try:
        member = await bot.get_chat_member(CHANNEL, user_id)

        if member.status in ["member", "administrator", "creator"]:
            await callback.message.answer(
                "📘 Qo'llanma:\n👉 https://youtu.be/RKblPCGf0TQ",
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