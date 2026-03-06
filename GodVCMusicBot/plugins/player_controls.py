from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from core.call import pause, resume, stop, skip_next
from core.queue import get_queue
from utils.thumbnail import generate_thumb
from utils.progress import pause_slider, resume_slider, stop_slider, seek_slider, reset_slider, build_keyboard, format_duration, start_slider, SLIDERS
import asyncio
import os

router = Router()

@router.callback_query()
async def controls(callback_query: types.CallbackQuery):
    chat_id = callback_query.message.chat.id if callback_query.message else None
    if callback_query.data in ("pause",) and chat_id:
        await pause(chat_id)
        await callback_query.answer("⏸ Paused")
        if callback_query.message:
            pause_slider(chat_id, callback_query.message.message_id)
    elif callback_query.data == "resume" and chat_id:
        await resume(chat_id)
        await callback_query.answer("▶ Resumed")
        if callback_query.message:
            resume_slider(chat_id, callback_query.message.message_id)
    elif callback_query.data == "skip" and chat_id:
        await callback_query.answer("⏭ Skipped")
        
        # Show skip animation
        frames = [
            "⏭ **Skipping Track...**\n\n▱▱▱▱▱▱▱▱▱",
            "⏭ **Skipping Track...**\n\n▰▱▱▱▱▱▱▱▱",
            "⏭ **Skipping Track...**\n\n▰▰▱▱▱▱▱▱▱",
            "⏭ **Skipping Track...**\n\n▰▰▰▱▱▱▱▱▱",
            "⏭ **Skipping Track...**\n\n▰▰▰▰▱▱▱▱▱",
            "⏭ **Skipping Track...**\n\n▰▰▰▰▰▱▱▱▱",
            "⏭ **Skipping Track...**\n\n▰▰▰▰▰▰▱▱▱",
            "⏭ **Skipping Track...**\n\n▰▰▰▰▰▰▰▱▱",
            "⏭ **Skipping Track...**\n\n▰▰▰▰▰▰▰▰▱",
            "⏭ **Skipping Track...**\n\n▰▰▰▰▰▰▰▰▰",
            "🎶 **Loading Next Song...**"
        ]
        
        for frame in frames:
            try:
                await callback_query.message.edit_text(frame)
                await asyncio.sleep(0.35)
            except Exception as e:
                if "FLOOD_WAIT" in str(e):
                    wait_time = int(str(e).split("_X] - A wait of ")[1].split(" seconds")[0]) if "_X] - A wait of " in str(e) else 5
                    await asyncio.sleep(wait_time + 1)
                    await callback_query.message.edit_text(frame)
                pass
        
        # Get next song from queue BEFORE skipping
        new_q = get_queue(chat_id)
        next_song = new_q[0] if len(new_q) > 0 else None
        
        # Skip to next song
        await skip_next(chat_id)
        
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
                msg = await callback_query.bot.send_photo(chat_id, photo=thumb_path, caption=caption, reply_markup=buttons)
                # Clean up thumbnail
                try:
                    os.remove(thumb_path)
                except:
                    pass
            except Exception as e:
                if "FLOOD_WAIT" in str(e):
                    await asyncio.sleep(12)
                    msg = await callback_query.bot.send_photo(chat_id, photo=thumb_path, caption=caption, reply_markup=buttons)
                    try:
                        os.remove(thumb_path)
                    except:
                        pass
                else:
                    raise
            
            # Start progress slider
            if duration_value:
                prefix = f"{header}\n{lines}"
                asyncio.create_task(start_slider(callback_query.bot, chat_id, msg.message_id, duration_value, prefix=prefix))
        else:
            await callback_query.message.edit_text(
                "Queue is empty! Nothing to skip to.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Close", callback_data="close")]])
            )
    elif callback_query.data == "stop" and chat_id:
        await stop(chat_id)
        await callback_query.answer("⏹ Stopped")
        if callback_query.message:
            stop_slider(chat_id, callback_query.message.message_id)
        user = callback_query.from_user.first_name if callback_query.from_user else "Unknown"
        text = f"➻ sᴛʀᴇᴀᴍ ᴇɴᴅᴇᴅ/sᴛᴏᴩᴩᴇᴅ 🎄\n│\n└ʙʏ : {user} 🥀"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✕ Close", callback_data="close")]])
        await callback_query.bot.send_message(chat_id, text, reply_markup=keyboard)
    elif callback_query.data == "seek_fwd_5" and chat_id and callback_query.message:
        seek_slider(chat_id, callback_query.message.message_id, 5)
        await callback_query.answer("↻ +5s")
        # Force immediate update of slider to show new position
        state_key = f"{chat_id}:{callback_query.message.message_id}"
        state = SLIDERS.get(state_key)
        if state:
            try:
                keyboard = build_keyboard(state["current"], state["duration"])
                await callback_query.bot.edit_message_caption(
                    chat_id=chat_id,
                    message_id=callback_query.message.message_id,
                    caption=state["prefix"],
                    reply_markup=keyboard
                )
            except Exception:
                pass
    elif callback_query.data == "seek_back_5" and chat_id and callback_query.message:
        seek_slider(chat_id, callback_query.message.message_id, -5)
        await callback_query.answer("↺ -5s")
        # Force immediate update of slider to show new position
        state_key = f"{chat_id}:{callback_query.message.message_id}"
        state = SLIDERS.get(state_key)
        if state:
            try:
                keyboard = build_keyboard(state["current"], state["duration"])
                await callback_query.bot.edit_message_caption(
                    chat_id=chat_id,
                    message_id=callback_query.message.message_id,
                    caption=state["prefix"],
                    reply_markup=keyboard
                )
            except Exception:
                pass
    elif callback_query.data == "prev":
        await callback_query.answer("⏮ Not implemented")
    elif callback_query.data == "loop":
        await callback_query.answer("🔁 Loop Enabled")
    elif callback_query.data == "shuffle":
        await callback_query.answer("🔀 Shuffle Enabled")
    elif callback_query.data == "close" and callback_query.message:
        await callback_query.message.delete()
    elif callback_query.data == "queue":
        await callback_query.answer("Queue shown")
    elif callback_query.data == "slider":
        await callback_query.answer("")
