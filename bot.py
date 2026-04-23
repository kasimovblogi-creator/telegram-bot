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
        "Assalamu alaykum, qo'llanmani olish uchun kanalga azo bo‘ling",
        reply_markup=sub_keyboard()
    )

# ================= SAVE ALL USERS =================
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
                "📘 Qo'llanmani ushbu havola orqali qo'lga kiriting 👇\n\https://youtu.be/RKblPCGf0TQ,
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