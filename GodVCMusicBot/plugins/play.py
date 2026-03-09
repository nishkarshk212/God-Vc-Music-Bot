from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.exceptions import TelegramRetryAfter
from core.queue import add_to_queue, get_queue
from core.ytdl import search_youtube, get_available_formats, download_song, get_direct_stream_link, resolve_stream
from utils.thumbnail import generate_thumb
from utils.format_selector import build_format_selection_menu, parse_callback_data
from core.call import start_playback, is_playing
from utils.progress import progress_bar, format_duration, start_slider, build_keyboard
from utils.logger import send_song_notification, get_voice_chat_participants, send_queue_added_notification
from utils.settings import get_chat_settings
import asyncio
import os

router = Router()

# Store pending format selections
pending_selections = {}

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
        from core.queue import get_queue, queue_manager
        
        # Check if VC ended - if so, clear status and allow fresh start
        if queue_manager.is_vc_ended(chat_id):
            queue_manager.unmark_vc_ended(chat_id)
            print(f"✅ Resetting VC ended status for chat {chat_id}")
        
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
    
    # Use quick play mode (default behavior)
    await quick_play(message, query)

@router.message(Command("playhd"))
async def play_hd(message: types.Message):
    """Advanced play with quality selection menu"""
    print(f"\n{'='*50}")
    print(f"🎬 HD PLAY COMMAND RECEIVED!")
    print(f"👤 User: {message.from_user.first_name}")
    print(f"💬 Chat: {message.chat.title}")
    print(f"{'='*50}\n")
    
    parts = message.text.split(None, 1)
    if len(parts) < 2:
        await message.answer("Send a song/video name after /playhd command.")
        return
    query = parts[1]
    
    status = await message.answer("🔎 Searching and analyzing formats...")
    
    try:
        # Search for the video
        info = await search_youtube(query)
        if not info:
            await status.edit_text("❌ No results found!")
            return
        
        title = info["title"]
        webpage_url = info.get("webpage_url")
        vidid = info.get("vidid")
        duration = info.get("duration", 0)
        
        # Get available formats
        formats_data = await get_available_formats(webpage_url or query)
        
        if not formats_data.get('success'):
            # Fallback to quick play if format extraction fails
            await status.edit_text("⚠️ Format analysis failed, using quick play...")
            await asyncio.sleep(2)
            await quick_play(message, query, status)
            return
        
        # Store pending selection
        pending_selections[message.from_user.id] = {
            'chat_id': message.chat.id,
            'query': query,
            'info': info,
            'formats': formats_data,
            'status_message': status
        }
        
        # Build format selection keyboard
        keyboard = build_format_selection_menu(vidid or str(hash(query)), title, duration)
        
        caption = f"""🎬 **Advanced Play Mode**

📀 **Title:** {title[:60]}
⏱️ **Duration:** {format_duration(duration)}
👤 **Requested by:** {message.from_user.first_name}

📊 **Available Qualities:** {len(formats_data.get('formats', {}))}

Select your preferred quality:"""
        
        await status.edit_text(caption, reply_markup=keyboard)
        
    except Exception as e:
        print(f"❌ HD Play error: {e}")
        import traceback
        traceback.print_exc()
        await status.edit_text(f"❌ Error: {str(e)[:200]}")

async def quick_play(message: types.Message, query: str, status_message: types.Message = None):
    """Quick play without format selection (original behavior)"""
    if not status_message:
        status = await message.answer("🔎 Searching Music...")
    else:
        status = status_message
    
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
    try:
        info = await search_youtube(query)
        if not info:
            await status.edit_text("❌ No results found. Try a different query or check spelling.")
            return
        
        title = info["title"]
        stream_url = info.get("url")
        thumb = info.get("thumbnail")
        webpage_url = info.get("webpage_url")
        vidid = info.get("vidid") or webpage_url.split('v=')[-1].split('&')[0] if webpage_url and 'v=' in webpage_url else None
        
        print(f"  → Found: {title}")
        print(f"  → URL: {webpage_url}")
        
        # ⚡ FAST PLAY OPTIMIZATION: Try direct stream FIRST (instant playback)
        file_path = None
        if webpage_url:
            print(f"  → Attempting direct stream resolution (FAST)...")
            try:
                resolved_url = await resolve_stream(webpage_url)
                if resolved_url:
                    file_path = resolved_url
                    print(f"  ✅ Got direct stream URL - INSTANT PLAY!")
            except Exception as resolve_err:
                print(f"  ⚠️ Stream resolution failed, downloading...")
        
        # Fallback to download only if stream fails
        if not file_path:
            print(f"  → Downloading audio (slower)...")
            file_path = await download_song(webpage_url or stream_url or query, quality="best", codec="h264")
        
        if not file_path:
            error_msg = "Could not get a playable file. This might be due to:\n\n"
            error_msg += "• YouTube blocking the server (IP Ban)\n"
            error_msg += "• Video is restricted or unavailable\n"
            error_msg += "• All extraction strategies failed"
            raise Exception(error_msg)

        # Verify local file one last time if it's a path
        if not str(file_path).startswith("http"):
            if not os.path.exists(file_path) or os.path.getsize(file_path) < 1000:
                print(f"❌ FINAL ERROR: File {file_path} is invalid or missing!")
                raise Exception("Downloaded file was corrupted or empty.")

        print(f"✅ Ready: {title}")
        print(f"🔗 Path/URL: {str(file_path)[:80]}...")
    except Exception as e:
        print(f"❌ ERROR preparing playback: {type(e).__name__}: {e}")
        # Silent failure - just delete status and return
        try:
            await status.delete()
        except:
            pass
        return
    
    # Check if already playing BEFORE adding to queue
    was_playing = is_playing(message.chat.id)
    
    item = {
        "title": title,
        "url": file_path, # Store the local path or resolved URL
        "thumbnail": thumb,
        "duration": info.get("duration"),
        "requester_id": message.from_user.id,
        "requester_name": message.from_user.first_name,
    }
    add_to_queue(message.chat.id, item)
    q = get_queue(message.chat.id)
    position = len(q) - 1
    if not was_playing:
        try:
            await status.edit_text("🎵 Connecting to Voice Chat and starting playback...")
            await start_playback(message.chat.id)
            print(f"🎵 Started playback in chat {message.chat.id}")
        except Exception as e:
            print(f"❌ Failed to start playback: {e}")
            await status.edit_text(f"❌ Failed to play music. Error: {str(e)[:100]}")
            # Remove the song from queue
            from core.queue import music_queue
            if music_queue.get(message.chat.id):
                music_queue[message.chat.id].pop()
            return
        
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
    header = "#𝟊єєℓ_𝚻нє_𝚸𝐨ω𝐞𝐫_𝐎𝐟_𝚳𝐮sî𝗰"
    lines = f"✯ 𝐓ɩttɭ𝛆 »   {title}\n✬ 𝐃ʋɽɑʈɩσŋ »  {duration_str}\n✭ 𝐁ɣ »  {message.from_user.first_name}"
    await status.delete()
    
    # Check if song was already playing (meaning this song is queued)
    if was_playing:
        # Song is queued - show queued message
        queue_caption = f"""
#𝟊єєℓ_𝚻нє_𝚸𝐨ω𝐞𝐫_𝐎𝐟_𝚳𝐮sî𝗰

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
