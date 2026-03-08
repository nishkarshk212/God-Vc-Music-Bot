from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.exceptions import TelegramRetryAfter
from core.call import skip_next, active_chats
from core.queue import get_queue
from utils.thumbnail import generate_thumb
from utils.progress import build_keyboard, format_duration, start_slider
from utils.logger import send_skip_notification
from utils.settings import get_chat_settings
import asyncio
import os

router = Router()

@router.message(Command("skip"))
async def skip_cmd(message: types.Message):
    chat_id = message.chat.id
    
    # Check skip mode permissions
    settings = get_chat_settings(chat_id)
    skip_mode = settings['skip_mode']
    
    user_id = message.from_user.id
    member = await message.bot.get_chat_member(chat_id, user_id)
    is_admin = member.status in ['administrator', 'creator']
    
    if skip_mode == "admin_only" and not is_admin:
        await message.answer("❌ Only administrators can use /skip command in this group.")
        return
    
    if skip_mode == "requester_only":
        # Check if user requested the current playing song
        from core.queue import get_queue
        q = get_queue(chat_id)
        current_song = q[0] if len(q) > 0 else None
        
        if current_song and isinstance(current_song, dict):
            requester_id = current_song.get('requester_id')
            if requester_id != user_id and not is_admin:
                await message.answer("❌ Only the person who requested this song can skip it.")
                return
        else:
            await message.answer("❌ No song is currently playing.")
            return
    
    # Get current playing song (to be skipped)
    current_q = get_queue(chat_id)
    current_song = current_q[0] if len(current_q) > 0 else None
    skipped_title = current_song.get("title", "Unknown") if current_song and isinstance(current_song, dict) else "Unknown"
    
    # Get next song from queue BEFORE skipping
    new_q = get_queue(chat_id)
    next_song = new_q[0] if len(new_q) > 0 else None
    
    await skip_next(chat_id)
    
    # Send skip notification to log channel immediately
    skip_info = {
        "requester_name": message.from_user.first_name,
        "requester_id": message.from_user.id,
        "requester_username": message.from_user.username if hasattr(message.from_user, 'username') else 'N/A',
        "chat_id": chat_id,
        "chat_title": message.chat.title,
        "chat_username": message.chat.username if hasattr(message.chat, 'username') else None,
        "skipped_title": skipped_title,
        "new_title": next_song.get("title", "Unknown") if next_song and isinstance(next_song, dict) else "Nothing"
    }
    asyncio.create_task(send_skip_notification(bot=message.bot, skip_info=skip_info))
    
    # Use the song we got before skipping
    if next_song and isinstance(next_song, dict):
        title = next_song.get("title", "Unknown")
        thumb_url = next_song.get("thumbnail", "")
        duration_value = next_song.get("duration", 0)
        requester = next_song.get("requester_name", "Unknown")
        
        # Generate thumbnail
        thumb_path = await generate_thumb(title, requester, thumb_url)
        
        # Build caption and controls
        duration_str = format_duration(duration_value)
        header = "#𝟊єєℓ_𝚻нє_𝚸𝐨ω𝐞𝗿_𝐎ƒ_𝚳𝐮sî𝗰"
        lines = f"✯ 𝐓ɩttɭ𝛆 »   {title}\n✬ 𝐃ʋɽɑʈɩσŋ »  {duration_str}\n✭ 𝐁ɣ »  {requester}"
        caption = f"{header}\n{lines}"
        buttons = build_keyboard(0, duration_value or 0)
        
        # Send playing message with thumbnail
        try:
            photo_file = FSInputFile(thumb_path)
            msg = await message.answer_photo(photo=photo_file, caption=caption, reply_markup=buttons)
            # Clean up thumbnail
            try:
                os.remove(thumb_path)
            except:
                pass
        except TelegramRetryAfter as e:
            wait_time = e.retry_after if hasattr(e, 'retry_after') else 3
            print(f"⏳ Flood control! Waiting {wait_time} seconds...")
            await asyncio.sleep(wait_time + 1)
            photo_file = FSInputFile(thumb_path)
            msg = await message.answer_photo(photo=photo_file, caption=caption, reply_markup=buttons)
            try:
                os.remove(thumb_path)
            except:
                pass
        except Exception as e:
            if "FLOOD_WAIT" in str(e):
                await asyncio.sleep(12)
                photo_file = FSInputFile(thumb_path)
                msg = await message.answer_photo(photo=photo_file, caption=caption, reply_markup=buttons)
                try:
                    os.remove(thumb_path)
                except:
                    pass
            else:
                raise
        
        # Start progress slider
        if duration_value:
            prefix = f"{header}\n{lines}"
            asyncio.create_task(start_slider(message.bot, chat_id, msg.message_id, duration_value, prefix=prefix))
    else:
        await message.answer("Queue is empty! Nothing to skip to.")
