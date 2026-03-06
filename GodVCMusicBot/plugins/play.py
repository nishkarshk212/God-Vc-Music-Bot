from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.exceptions import TelegramRetryAfter
from core.queue import add_to_queue, get_queue
from core.ytdl import search_youtube
from utils.thumbnail import generate_thumb
from core.call import start_playback, is_playing
from utils.progress import progress_bar, format_duration, start_slider, build_keyboard
from utils.logger import send_song_notification, get_voice_chat_participants, send_queue_added_notification
from utils.settings import get_chat_settings
import asyncio
import os

router = Router()

@router.message(Command("play"))
async def play(message: types.Message):
    print(f"\n{'='*50}")
    print(f"📨 COMMAND RECEIVED!")
    print(f"👤 User: {message.from_user.first_name} (@{message.from_user.username})")
    print(f"💬 Chat: {message.chat.title} (ID: {message.chat.id})")
    print(f"📝 Text: {message.text}")
    print(f"{'='*50}\n")
    
    # Check play mode permissions
    chat_id = message.chat.id
    settings = get_chat_settings(chat_id)
    play_mode = settings['play_mode']
    
    user_id = message.from_user.id
    member = await message.bot.get_chat_member(chat_id, user_id)
    is_admin = member.status in ['administrator', 'creator']
    
    if play_mode == "admin_only" and not is_admin:
        await message.answer("❌ Only administrators can use /play command in this group.")
        return
    
    if play_mode == "requester_only":
        # Check if user is currently playing or has songs in queue
        from core.call import active_chats
        from core.queue import get_queue
        q = get_queue(chat_id)
        user_has_song = any(item.get('requester_id') == user_id for item in q if isinstance(item, dict))
        
        if chat_id not in active_chats and not user_has_song:
            await message.answer("❌ Only users who have played songs can use /play in this group.")
            return
    
    parts = message.text.split(None, 1)
    if len(parts) < 2:
        await message.answer("Send a song name after the command.")
        return
    query = parts[1]
    print(f"\n🎵 /play command received from {message.from_user.first_name}")
    print(f"🔍 Searching for: {query}")
    status = await message.answer("🔎 Searching Music...")
    await asyncio.sleep(1)
    frames = ["🎵 ▰▱▱▱▱ Loading", "🎵 ▰▰▱▱▱ Loading", "🎵 ▰▰▰▱▱ Loading", "🎵 ▰▰▰▰▱ Loading", "🎵 ▰▰▰▰▰ Loading"]
    for frame in frames:
        await asyncio.sleep(0.5)
        try:
            await status.edit_text(frame)
        except Exception as e:
            if "FLOOD_WAIT" in str(e):
                wait_time = int(str(e).split("_X] - A wait of ")[1].split(" seconds")[0]) if "_X] - A wait of " in str(e) else 5
                await asyncio.sleep(wait_time + 1)
                await status.edit_text(frame)
            pass
    try:
        await status.edit_text("🎧 Connecting to Voice Chat...")
    except Exception as e:
        if "FLOOD_WAIT" in str(e):
            wait_time = int(str(e).split("_X] - A wait of ")[1].split(" seconds")[0]) if "_X] - A wait of " in str(e) else 5
            await asyncio.sleep(wait_time + 1)
            await status.edit_text("🎧 Connecting to Voice Chat...")
        pass
    await asyncio.sleep(1)
    try:
        await status.edit_text("🎶 Starting Stream...")
    except Exception as e:
        if "FLOOD_WAIT" in str(e):
            wait_time = int(str(e).split("_X] - A wait of ")[1].split(" seconds")[0]) if "_X] - A wait of " in str(e) else 5
            await asyncio.sleep(wait_time + 1)
            await status.edit_text("🎶 Starting Stream...")
        pass
    await asyncio.sleep(1)
    print(f"📥 Getting info from YouTube...")
    info = search_youtube(query)
    title = info["title"]
    stream_url = info["url"]
    thumb = info["thumbnail"]
    print(f"✅ Found: {title}")
    print(f"🔗 Stream URL: {stream_url[:80]}...")
    
    # Check if already playing BEFORE adding to queue
    was_playing = is_playing(message.chat.id)
    
    item = {
        "title": title,
        "url": stream_url,
        "thumbnail": thumb,
        "duration": info.get("duration"),
        "requester_id": message.from_user.id,
        "requester_name": message.from_user.first_name,
    }
    add_to_queue(message.chat.id, item)
    position = len(get_queue(message.chat.id))
    if not was_playing:
        await start_playback(message.chat.id)
        print(f"🎵 Started playback in chat {message.chat.id}")
        
        # Get voice chat participants
        vc_participants = await get_voice_chat_participants(message.bot, message.chat.id)
        
        # Send notification to log channel for the first song being played
        song_info = {
            "title": title,
            "requester_name": message.from_user.first_name,
            "requester_id": message.from_user.id,
            "requester_username": message.from_user.username if hasattr(message.from_user, 'username') else 'N/A',
            "chat_id": message.chat.id,
            "chat_title": message.chat.title,
            "chat_username": message.chat.username if hasattr(message.chat, 'username') else None,
            "vc_participants": vc_participants
        }
        asyncio.create_task(send_song_notification(bot=message.bot, song_info=song_info))
    else:
        print(f"⏸ Song added to queue (position #{position})")
        
        # Send queue added notification to log channel
        duration_str = format_duration(info.get("duration"))
        queue_info = {
            "title": title,
            "requester_name": message.from_user.first_name,
            "requester_id": message.from_user.id,
            "requester_username": message.from_user.username if hasattr(message.from_user, 'username') else 'N/A',
            "chat_id": message.chat.id,
            "chat_title": message.chat.title,
            "chat_username": message.chat.username if hasattr(message.chat, 'username') else None,
            "duration_str": duration_str,
            "position": position
        }
        asyncio.create_task(send_queue_added_notification(bot=message.bot, song_info=queue_info))
    duration_value = info.get("duration")
    buttons = build_keyboard(0, duration_value or 0)
    thumb_path = await generate_thumb(title, message.from_user.first_name, thumb)
    duration_str = format_duration(duration_value)
    header = "#𝟊єєℓ_𝚻нє_𝚸𝐨ω𝐞𝗿_𝐎ƒ_𝚳𝐮sî𝗰"
    lines = f"✯ 𝐓ɩttɭ𝛆 »   {title}\n✬ 𝐃ʋɽɑʈɩσŋ »  {duration_str}\n✭ 𝐁ɣ »  {message.from_user.first_name}"
    await status.delete()
    
    # Check if song was already playing (meaning this song is queued)
    if was_playing:
        # Song is queued - show queued message
        queue_caption = f"""
#𝟊єєℓ_𝚻нє_𝚸𝐨ω𝐞𝗿_𝐎ƒ_𝚳𝐮sî𝗰

✯ 𝐓ɩttɭ𝛆 »   {title}
✬ 𝐃ʋɽɑʈɩσŋ »  {duration_str}
✭ 𝐁ɣ » {message.from_user.first_name}
✭ 𝒒𝒖𝒆𝒖𝒆  » #{position}

⏳ Please wait for your turn...
"""
        close_keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✕ Close", callback_data="close")]])
        try:
            await message.answer(queue_caption, reply_markup=close_keyboard)
        except TelegramRetryAfter as e:
            # Handle flood control - wait the specified time and retry
            wait_time = e.retry_after if hasattr(e, 'retry_after') else 3
            print(f"⏳ Flood control! Waiting {wait_time} seconds...")
            await asyncio.sleep(wait_time + 1)
            await message.answer(queue_caption, reply_markup=close_keyboard)
        except Exception as e:
            if "FLOOD_WAIT" in str(e):
                await asyncio.sleep(12)
                await message.answer(queue_caption, reply_markup=close_keyboard)
            else:
                raise
    else:
        # First song or nothing playing - show full player with controls, thumbnail and slider
        caption = f"{header}\n{lines}"
        try:
            # Send as photo message with generated thumbnail
            photo_file = FSInputFile(thumb_path)
            msg = await message.answer_photo(photo=photo_file, caption=caption, reply_markup=buttons)
            # Clean up thumbnail file after sending
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
        if duration_value:
            prefix = f"{header}\n{lines}"
            asyncio.create_task(start_slider(message.bot, message.chat.id, msg.message_id, duration_value, prefix=prefix))
