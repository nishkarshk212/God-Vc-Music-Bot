from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from core.call import stop
from core.queue import get_queue
from utils.logger import send_stop_notification
from utils.settings import get_chat_settings
import asyncio

router = Router()

@router.message(Command("stop"))
async def stop_cmd(message: types.Message):
    chat_id = message.chat.id
    
    # Check stop mode permissions
    settings = get_chat_settings(chat_id)
    stop_mode = settings['stop_mode']
    
    user_id = message.from_user.id
    member = await message.bot.get_chat_member(chat_id, user_id)
    is_admin = member.status in ['administrator', 'creator']
    
    if stop_mode == "admin_only" and not is_admin:
        await message.answer("❌ Only administrators can use /stop command in this group.")
        return
    
    if stop_mode == "requester_only":
        # Check if user requested the current playing song
        from core.queue import get_queue
        q = get_queue(chat_id)
        current_song = q[0] if len(q) > 0 else None
        
        if current_song and isinstance(current_song, dict):
            requester_id = current_song.get('requester_id')
            if requester_id != user_id and not is_admin:
                await message.answer("❌ Only the person who requested this song can stop it.")
                return
        else:
            await message.answer("❌ No song is currently playing.")
            return
    
    msg = await message.answer("⏹ Initiating Music Shutdown...")
    
    frames = [
        "🎶 𝙎𝙩𝙤𝙥𝙥𝙞𝙣𝙜 𝙖𝙪𝙙𝙞𝙤 𝙨𝙩𝙧𝙚𝙖𝙢\n\n▰▱▱▱▱",
        "🎶 𝙎𝙩𝙤𝙥𝙥𝙞𝙣𝙜 𝙖𝙪𝙙𝙞𝙤 𝙨𝙩𝙧𝙚𝙖𝙢\n\n▰▰▱▱▱",
        "🎶 𝙎𝙩𝙤𝙥𝙥𝙞𝙣𝙜 𝙖𝙪𝙙𝙞𝙤 𝙨𝙩𝙧𝙚𝙖𝙢\n\n▰▰▰▱▱",
        "🎶 𝙎𝙩𝙤𝙥𝙥𝙞𝙣𝙜 𝙖𝙪𝙙𝙞𝙤 𝙨𝙩𝙧𝙚𝙖𝙢\n\n▰▰▰▰▱",
        "🎶 𝙎𝙩𝙤𝙥𝙥𝙞𝙣𝙜 𝙖𝙪𝙙𝙞𝙤 𝙨𝙩𝙧𝙚𝙖𝙢\n\n▰▰▰▰▰"
    ]
    
    for frame in frames:
        await asyncio.sleep(0.6)
        try:
            await msg.edit_text(frame)
        except Exception as e:
            if "FLOOD_WAIT" in str(e):
                wait_time = int(str(e).split("_X] - A wait of ")[1].split(" seconds")[0]) if "_X] - A wait of " in str(e) else 5
                await asyncio.sleep(wait_time + 1)
                await msg.edit_text(frame)
            pass
    
    try:
        await msg.edit_text("🧹 Clearing Queue...")
    except Exception as e:
        if "FLOOD_WAIT" in str(e):
            wait_time = int(str(e).split("_X] - A wait of ")[1].split(" seconds")[0]) if "_X] - A wait of " in str(e) else 5
            await asyncio.sleep(wait_time + 1)
            await msg.edit_text("🧹 Clearing Queue...")
        pass
    await asyncio.sleep(1)
    
    try:
        await msg.edit_text("🔌 Disconnecting Voice Chat...")
    except Exception as e:
        if "FLOOD_WAIT" in str(e):
            wait_time = int(str(e).split("_X] - A wait of ")[1].split(" seconds")[0]) if "_X] - A wait of " in str(e) else 5
            await asyncio.sleep(wait_time + 1)
            await msg.edit_text("🔌 Disconnecting Voice Chat...")
        pass
    await asyncio.sleep(1)
    
    # Get current playing song before stopping
    current_q = get_queue(message.chat.id)
    last_song = current_q[0] if len(current_q) > 0 else None
    last_title = last_song.get("title", "Unknown") if last_song and isinstance(last_song, dict) else "Unknown"
    
    # Stop VC stream
    await stop(message.chat.id)
    
    # Send stop notification to log channel
    stop_info = {
        "requester_name": message.from_user.first_name,
        "requester_id": message.from_user.id,
        "requester_username": message.from_user.username if hasattr(message.from_user, 'username') else 'N/A',
        "chat_id": message.chat.id,
        "chat_title": message.chat.title,
        "chat_username": message.chat.username if hasattr(message.chat, 'username') else None,
        "last_title": last_title
    }
    asyncio.create_task(send_stop_notification(bot=message.bot, stop_info=stop_info))
    
    user = message.from_user.first_name if message.from_user else "Unknown"
    final_text = f"""
✅ 𝙈𝙪𝙨𝙞𝙘 𝙋𝙡𝙖𝙮𝙚𝙧 𝙎𝙩𝙤𝙥𝙥𝙚𝙙

➻ sᴛʀᴇᴀᴍ ᴇɴᴅᴇᴅ/sᴛᴏᴩᴩᴇᴅ 🎄
│
└ʙʏ : {user} 🥀

🎧 Voice Chat Disconnected  
📭 Queue Cleared

Use /𝒑𝒍𝒂𝒚 to start music again.
"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✕ Close", callback_data="close")]])
    await msg.edit_text(final_text, reply_markup=keyboard)
