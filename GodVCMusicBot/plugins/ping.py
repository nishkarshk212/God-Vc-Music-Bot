from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command("ping"))
async def ping(message: types.Message):
    print(f"\n✅ PING command received from {message.from_user.first_name}")
    await message.answer(f"🏓 Pong! Bot is working!\n\nBot is ready to play music.\nUse /play <song_name>")
