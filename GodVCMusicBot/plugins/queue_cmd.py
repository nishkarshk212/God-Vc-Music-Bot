from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from core.queue import get_queue

router = Router()

@router.message(Command("queue"))
async def show_queue(message: types.Message):
    q = get_queue(message.chat.id)
    if not q:
        await message.answer("Queue is empty.")
        return
    def line(i, item):
        title = item["title"] if isinstance(item, dict) and "title" in item else str(item)
        by = item.get("requester_name") if isinstance(item, dict) else None
        base = f"{i+1}. {title}"
        return f"{base} — by {by}" if by else base
    text = "\n".join([line(i, item) for i, item in enumerate(q)])
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✕ Close", callback_data="close")]])
    await message.answer(text, reply_markup=keyboard)
