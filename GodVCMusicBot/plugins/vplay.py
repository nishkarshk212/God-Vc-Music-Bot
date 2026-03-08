from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from core.queue import add_to_queue, get_queue
from core.ytdl import search_youtube_video
from utils.thumbnail import generate_thumb
from core.call import start_playback_video, is_playing
from utils.progress import progress_bar, format_duration, start_slider, build_keyboard
from utils.logger import send_song_notification, get_voice_chat_participants
import asyncio
import os

router = Router()

@router.message(Command("vplay"))
async def vplay(message: types.Message):
    parts = message.text.split(None, 1)
    if len(parts) < 2:
        await message.answer("Send a video name after the command.")
        return
    query = parts[1]
    status = await message.answer("🔎 Searching Video...")
    await asyncio.sleep(1)
    frames = ["🎬 ▰▱▱▱▱ Loading", "🎬 ▰▰▱▱▱ Loading", "🎬 ▰▰▰▱▱ Loading", "🎬 ▰▰▰▰▱ Loading", "🎬 ▰▰▰▰▰ Loading"]
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
        await status.edit_text("📺 Starting Video Stream...")
    except Exception as e:
        if "FLOOD_WAIT" in str(e):
            wait_time = int(str(e).split("_X] - A wait of ")[1].split(" seconds")[0]) if "_X] - A wait of " in str(e) else 5
            await asyncio.sleep(wait_time + 1)
            await status.edit_text("📺 Starting Video Stream...")
        pass
    await asyncio.sleep(1)
    info = await search_youtube_video(query)
    title = info["title"]
    stream_url = info.get("url")
    thumb = info.get("thumbnail")
    webpage_url = info.get("webpage_url")

    # Strategy: Download first for stability (Done silently in background)
    from core.ytdl import download_video
    file_path = await download_video(webpage_url or stream_url or query)

    if not file_path:
        # Resolve stream URL if download missing
        if not stream_url and webpage_url:
            print(f"  → Video stream URL missing, resolving from {webpage_url}...")
            from core.ytdl import resolve_stream
            try:
                stream_url = await resolve_stream(webpage_url)
            except Exception as resolve_err:
                print(f"❌ Video resolution failed: {resolve_err}")
                stream_url = webpage_url
        file_path = stream_url

    if not file_path:
        await status.edit_text("❌ Failed to find or download the video. Please try again.")
        return
    
    # Check if already playing BEFORE adding to queue
    was_playing = is_playing(message.chat.id)
    
    item = {
        "title": title,
        "url": file_path,
        "thumbnail": thumb,
        "duration": info.get("duration"),
        "requester_id": message.from_user.id,
        "requester_name": message.from_user.first_name,
        "is_video": True,
    }
    add_to_queue(message.chat.id, item)
    if not was_playing:
        await start_playback_video(message.chat.id)
        print(f"🎬 Started video playback in chat {message.chat.id}")
        
        # Get voice chat participants
        vc_participants = await get_voice_chat_participants(message.bot, message.chat.id)
        
        # Send notification to log channel for the first video being played
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
        print(f"⏸ Video added to queue (position #{position})")
    duration_value = info.get("duration")
    buttons = build_keyboard(0, duration_value or 0)
    thumb_path = await generate_thumb(title, message.from_user.first_name, thumb)
    duration_str = format_duration(duration_value)
    header = "#𝟊єєℓ_𝚻нє_𝚸𝐨ω𝐞𝗿_𝐎ƒ_𝚳𝐮sî𝗰"
    lines = f"✯ 𝐓ɩttɭ𝛆 »   {title}\n✬ 𝐃ʋɽɑʈɩσŋ »  {duration_str}\n✭ 𝐁ɣ »  {message.from_user.first_name}"
    await status.delete()
    position = len(get_queue(message.chat.id))
    
    # Check if video was already playing (meaning this video is queued)
    if was_playing:
        # Video is queued - show queued message
        queue_caption = f"""
📥 **Video Added To Queue**

🎬 **Title:** {title}
⏱ **Duration:** {duration_str}
👤 **Requested by:** {message.from_user.first_name}
📊 **Position:** #{position}

⏳ Please wait for your turn...
"""
        close_keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✕ Close", callback_data="close")]])
        try:
            await message.answer(queue_caption, reply_markup=close_keyboard)
        except Exception as e:
            if "FLOOD_WAIT" in str(e):
                await asyncio.sleep(12)
                await message.answer(queue_caption, reply_markup=close_keyboard)
            else:
                raise
    else:
        # First video or nothing playing - show full player with controls, thumbnail and slider
        caption = f"{header}\n{lines}"
        try:
            # Send as photo message with generated thumbnail
            msg = await message.answer_photo(photo=thumb_path, caption=caption, reply_markup=buttons)
            # Clean up thumbnail file after sending
            try:
                os.remove(thumb_path)
            except:
                pass
        except Exception as e:
            if "FLOOD_WAIT" in str(e):
                await asyncio.sleep(12)
                msg = await message.answer_photo(photo=thumb_path, caption=caption, reply_markup=buttons)
                try:
                    os.remove(thumb_path)
                except:
                    pass
            else:
                raise
        if duration_value:
            prefix = f"{header}\n{lines}"
            asyncio.create_task(start_slider(message.bot, message.chat.id, msg.message_id, duration_value, prefix=prefix))
