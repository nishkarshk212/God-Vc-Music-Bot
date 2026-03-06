import logging
from aiogram import Bot
from config import BOT_TOKEN, LOG_CHANNEL_ID


class TelegramLogHandler(logging.Handler):
    """Custom logging handler that sends logs to Telegram channel"""
    
    def __init__(self, bot: Bot, chat_id: str):
        super().__init__()
        self.bot = bot
        self.chat_id = chat_id
        self.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
    
    async def send_to_telegram(self, message: str):
        """Send log message to Telegram channel"""
        try:
            if self.chat_id:
                await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=f"<code>{message}</code>",
                    parse_mode='HTML'
                )
        except Exception as e:
            # Silently ignore errors to prevent infinite loops
            pass
    
    def emit(self, record):
        """Emit a log record"""
        try:
            msg = self.format(record)
            # Create a new event loop for sending the message
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            if loop.is_running():
                # If loop is running, schedule the coroutine
                asyncio.create_task(self.send_to_telegram(msg))
            else:
                # If loop is not running, run it
                loop.run_until_complete(self.send_to_telegram(msg))
        except Exception:
            self.handleError(record)


def setup_logging(bot: Bot):
    """Configure logging to suppress terminal output"""
    
    # Get root logger
    root_logger = logging.getLogger()
    
    # Remove existing handlers (console handlers)
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Set log level
    root_logger.setLevel(logging.CRITICAL)  # Suppress all logs
    
    print(f"✅ Terminal logging suppressed")
    
    return root_logger


async def get_voice_chat_participants(client, chat_id: int):
    """Get list of participants in voice chat"""
    try:
        from hydrogram.types import Chat
        # Get voice chat participants using PyTgCalls
        participants = []
        
        # Try to get participants from the call
        try:
            # Get current call if exists
            from assistant import call_py
            members = await call_py.get_participants(chat_id)
            for member in members:
                participants.append({
                    "id": member.id,
                    "first_name": member.first_name,
                    "username": member.username if member.username else "N/A"
                })
        except:
            pass
        
        return participants
    except Exception as e:
        return []


async def send_log_notification(bot: Bot, action_type: str, details: dict):
    """Send any log notification to the channel
    
    Args:
        bot: Bot instance
        action_type: Type of action (play, queue_add, skip, stop, etc.)
        details: Dictionary with action details
    """
    if not LOG_CHANNEL_ID:
        return
    
    try:
        # Build group link
        chat_username = details.get('chat_username')
        chat_id = details.get('chat_id')
        if chat_username:
            group_link = f"https://t.me/{chat_username}"
        else:
            group_link = f"https://t.me/joinchat/{chat_id}"
        
        # Build user link
        user_id = details.get('requester_id')
        user_link = f"tg://user?id={user_id}" if user_id else "#"
        
        await bot.send_message(
            chat_id=LOG_CHANNEL_ID,
            text=details.get('message', ''),
            parse_mode='HTML',
            disable_web_page_preview=True
        )
    except Exception as e:
        pass


async def send_song_notification(bot: Bot, song_info: dict):
    """Send song play notification to the log channel
    
    Args:
        bot: Bot instance
        song_info: Dictionary containing:
            - title: Song title
            - requester_name: Who played the song
            - requester_id: User ID who played
            - requester_username: Username of requester
            - chat_id: Group ID where it was played
            - chat_title: Group name
            - chat_username: Group username (if available)
            - vc_participants: List of voice chat participants (optional)
    """
    if not LOG_CHANNEL_ID:
        return
    
    try:
        # Build group link
        chat_username = song_info.get('chat_username')
        chat_id = song_info.get('chat_id')
        if chat_username:
            group_link = f"https://t.me/{chat_username}"
        else:
            group_link = f"https://t.me/joinchat/{chat_id}"
        
        # Build user link
        user_id = song_info.get('requester_id')
        user_link = f"tg://user?id={user_id}"
        
        # Count voice chat participants
        vc_count = len(song_info.get('vc_participants', []))
        
        # Format notification message with enhanced user info
        caption = f"""
🎵 <b>NEW SONG PLAYED</b> 🎵

👤 <b>Played by:</b> <a href="{user_link}">{song_info['requester_name']}</a>
🆔 <b>User ID:</b> <code>{song_info['requester_id']}</code>
📛 <b>Username:</b> @{song_info.get('requester_username', 'N/A')}

📍 <b>In Group:</b> {song_info['chat_title']}
🆔 <b>Group ID:</b> <code>{chat_id}</code>
🔗 <b>Group Link:</b> <a href="{group_link}">Click Here</a>

🎶 <b>Song Title:</b> {song_info['title']}

🎙️ <b>Voice Chat Stats:</b>
👥 <b>Members in VC:</b> {vc_count}
"""
        
        # Add participant list if available
        if song_info.get('vc_participants'):
            participants_text = "\n".join([
                f"• <a href=\"tg://user?id={p['id']}\">{p['first_name']}</a>" 
                for p in song_info['vc_participants'][:10]  # Limit to first 10
            ])
            if len(song_info['vc_participants']) > 10:
                participants_text += f"\n... and {len(song_info['vc_participants']) - 10} more"
            
            caption += f"\n<b>Participants:</b>\n{participants_text}"
        
        await bot.send_message(
            chat_id=LOG_CHANNEL_ID,
            text=caption,
            parse_mode='HTML',
            disable_web_page_preview=True
        )
    except Exception as e:
        pass


async def send_queue_added_notification(bot: Bot, song_info: dict):
    """Send queue added notification to log channel"""
    if not LOG_CHANNEL_ID:
        return
    
    try:
        chat_username = song_info.get('chat_username')
        chat_id = song_info.get('chat_id')
        if chat_username:
            group_link = f"https://t.me/{chat_username}"
        else:
            group_link = f"https://t.me/joinchat/{chat_id}"
        
        user_id = song_info.get('requester_id')
        user_link = f"tg://user?id={user_id}"
        
        caption = f"""
📥 <b>SONG ADDED TO QUEUE</b> 📥

👤 <b>Added by:</b> <a href="{user_link}">{song_info['requester_name']}</a>
🆔 <b>User ID:</b> <code>{song_info['requester_id']}</code>
📛 <b>Username:</b> @{song_info.get('requester_username', 'N/A')}

📍 <b>Group:</b> {song_info['chat_title']}
🆔 <b>Group ID:</b> <code>{chat_id}</code>
🔗 <b>Group Link:</b> <a href="{group_link}">Click Here</a>

🎶 <b>Song:</b> {song_info['title']}
⏱ <b>Duration:</b> {song_info.get('duration_str', 'Unknown')}
📊 <b>Position:</b> #{song_info.get('position', 'N/A')}

<b>Status:</b> ⏳ Queued
"""
        
        await bot.send_message(
            chat_id=LOG_CHANNEL_ID,
            text=caption,
            parse_mode='HTML',
            disable_web_page_preview=True
        )
    except Exception as e:
        pass


async def send_skip_notification(bot: Bot, skip_info: dict):
    """Send track skipped notification to log channel"""
    if not LOG_CHANNEL_ID:
        return
    
    try:
        chat_username = skip_info.get('chat_username')
        chat_id = skip_info.get('chat_id')
        if chat_username:
            group_link = f"https://t.me/{chat_username}"
        else:
            group_link = f"https://t.me/joinchat/{chat_id}"
        
        user_id = skip_info.get('requester_id')
        user_link = f"tg://user?id={user_id}"
        
        caption = f"""
⏭️ <b>TRACK SKIPPED</b> ⏭️

👤 <b>Skipped by:</b> <a href="{user_link}">{skip_info['requester_name']}</a>
🆔 <b>User ID:</b> <code>{skip_info['requester_id']}</code>
📛 <b>Username:</b> @{skip_info.get('requester_username', 'N/A')}

📍 <b>Group:</b> {skip_info['chat_title']}
🆔 <b>Group ID:</b> <code>{chat_id}</code>
🔗 <b>Group Link:</b> <a href="{group_link}">Click Here</a>

❌ <b>Skipped Track:</b> {skip_info.get('skipped_title', 'Unknown')}
▶️ <b>Now Playing:</b> {skip_info.get('new_title', 'Nothing')}

<b>Action:</b> ⏩ Skip to Next
"""
        
        await bot.send_message(
            chat_id=LOG_CHANNEL_ID,
            text=caption,
            parse_mode='HTML',
            disable_web_page_preview=True
        )
    except Exception as e:
        pass


async def send_stop_notification(bot: Bot, stop_info: dict):
    """Send music stopped notification to log channel"""
    if not LOG_CHANNEL_ID:
        return
    
    try:
        chat_username = stop_info.get('chat_username')
        chat_id = stop_info.get('chat_id')
        if chat_username:
            group_link = f"https://t.me/{chat_username}"
        else:
            group_link = f"https://t.me/joinchat/{chat_id}"
        
        user_id = stop_info.get('requester_id')
        user_link = f"tg://user?id={user_id}"
        
        caption = f"""
⏹️ <b>MUSIC STOPPED</b> ⏹️

👤 <b>Stopped by:</b> <a href="{user_link}">{stop_info['requester_name']}</a>
🆔 <b>User ID:</b> <code>{stop_info['requester_id']}</code>
📛 <b>Username:</b> @{stop_info.get('requester_username', 'N/A')}

📍 <b>Group:</b> {stop_info['chat_title']}
🆔 <b>Group ID:</b> <code>{chat_id}</code>
🔗 <b>Group Link:</b> <a href="{group_link}">Click Here</a>

🎶 <b>Last Track:</b> {stop_info.get('last_title', 'Unknown')}

<b>Status:</b> ❌ Stopped
🧹 <b>Queue:</b> Cleared
🔌 <b>Voice Chat:</b> Disconnected
"""
        
        await bot.send_message(
            chat_id=LOG_CHANNEL_ID,
            text=caption,
            parse_mode='HTML',
            disable_web_page_preview=True
        )
    except Exception as e:
        pass
