import logging
from aiogram import Bot
from config import BOT_TOKEN, LOG_CHANNEL_ID

def setup_logging(bot: Bot):
    """Configure logging to show important info and errors"""
    
    # Get root logger
    root_logger = logging.getLogger()
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Set log level to INFO
    root_logger.setLevel(logging.INFO)
    
    # Add a console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    root_logger.addHandler(console_handler)
    
    print(f"✅ Logging configured (INFO level)")
    
    return root_logger

async def get_voice_chat_participants(client, chat_id: int):
    try:
        from assistant import call_py
        participants = []
        try:
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
    except:
        return []

async def send_log_notification(bot: Bot, action_type: str, details: dict):
    if not LOG_CHANNEL_ID:
        return
    try:
        await bot.send_message(chat_id=LOG_CHANNEL_ID, text=details.get('message', ''))
    except:
        pass

async def send_song_notification(bot: Bot, song_info: dict):
    """Send detailed song playback notification to log channel"""
    # Send to both LOG_CHANNEL_ID and @logx_212
    log_channels = []
    if LOG_CHANNEL_ID:
        log_channels.append(LOG_CHANNEL_ID)
    log_channels.append("@logx_212")  # Additional log channel
    
    if not log_channels:
        return
    
    try:
        user_id = song_info.get('requester_id')
        user_link = f"tg://user?id={user_id}"
        username = song_info.get('requester_username', 'N/A')
        username_text = f"@{username}" if username != 'N/A' else 'N/A'
        
        # Get group information
        chat_id = song_info.get('chat_id')
        chat_title = song_info.get('chat_title', 'Unknown')
        chat_username = song_info.get('chat_username')
        
        # Create group link
        if chat_username:
            group_link = f"https://t.me/{chat_username}"
        else:
            group_link = f"https://t.me/+{chat_id}"
        
        # Get voice chat participants count and details
        vc_participants = song_info.get('vc_participants', [])
        vc_count = len(vc_participants)
        
        # Build participants list
        participants_text = ""
        if vc_count > 0:
            participants_text = "\n\n👥 <b>Voice Chat Participants:</b>\n"
            for i, participant in enumerate(vc_participants[:10], 1):  # Show first 10
                p_name = participant.get('first_name', 'Unknown')
                p_username = participant.get('username', 'N/A')
                p_id = participant.get('id')
                p_mention = f"<a href='tg://user?id={p_id}'>{p_name}</a>"
                if p_username != 'N/A':
                    participants_text += f"\n{i}. {p_mention} (@{p_username})"
                else:
                    participants_text += f"\n{i}. {p_mention}"
            
            if vc_count > 10:
                participants_text += f"\n... and {vc_count - 10} more"
        else:
            participants_text = "\n\n👥 <b>Voice Chat Participants:</b> None (Bot is alone)"
        
        # Get detailed group info
        try:
            chat_info = await bot.get_chat(chat_id)
            members_count = chat_info.members_count if hasattr(chat_info, 'members_count') else 'Unknown'
            chat_type = chat_info.type if hasattr(chat_info, 'type') else 'Unknown'
            chat_description = chat_info.description if hasattr(chat_info, 'description') and chat_info.description else 'No description'
            
            group_info_text = f"""\n\n📊 <b>Group Information:</b>
🏷️ <b>Name:</b> {chat_title}
🆔 <b>ID:</b> <code>{chat_id}</code>
👥 <b>Total Members:</b> {members_count}
📝 <b>Type:</b> {chat_type}
📢 <b>Username:</b> @{chat_username if chat_username else 'Private Group'}
📋 <b>Description:</b> {chat_description[:100]}{'...' if len(chat_description) > 100 else ''}"""
        except:
            group_info_text = f"""\n\n📊 <b>Group Information:</b>
🏷️ <b>Name:</b> {chat_title}
🆔 <b>ID:</b> <code>{chat_id}</code>
📢 <b>Username:</b> @{chat_username if chat_username else 'Private Group'}"""
        
        # Build detailed caption
        caption = f"""🎵 <b>NEW SONG PLAYING</b> 🎵

🎶 <b>Title:</b> {song_info['title']}
👤 <b>Requested by:</b> <a href='{user_link}'>{song_info['requester_name']}</a>
🆔 <b>User ID:</b> <code>{user_id}</code>
📛 <b>Username:</b> {username_text}
💬 <b>Group:</b> {chat_title}
🔗 <b>Group Link:</b> <a href='{group_link}'>View Group</a>
👥 <b>VC Members:</b> {vc_count}{participants_text}{group_info_text}

#NowPlaying #MusicLog"""
        
        # Send to all configured channels
        for channel in log_channels:
            try:
                await bot.send_message(chat_id=channel, text=caption, parse_mode='HTML', disable_web_page_preview=True)
            except Exception as channel_error:
                print(f"Failed to send to channel {channel}: {channel_error}")
                
    except Exception as e:
        print(f"Failed to send song notification: {e}")
        import traceback
        traceback.print_exc()

async def send_queue_added_notification(bot: Bot, song_info: dict):
    """Send detailed queue added notification to log channel"""
    # Send to both LOG_CHANNEL_ID and @logx_212
    log_channels = []
    if LOG_CHANNEL_ID:
        log_channels.append(LOG_CHANNEL_ID)
    log_channels.append("@logx_212")  # Additional log channel
    
    if not log_channels:
        return
    
    try:
        user_id = song_info.get('requester_id')
        user_link = f"tg://user?id={user_id}"
        username = song_info.get('requester_username', 'N/A')
        username_text = f"@{username}" if username != 'N/A' else 'N/A'
        
        # Get group information
        chat_id = song_info.get('chat_id')
        chat_title = song_info.get('chat_title', 'Unknown')
        chat_username = song_info.get('chat_username')
        
        # Create group link
        if chat_username:
            group_link = f"https://t.me/{chat_username}"
        else:
            group_link = f"https://t.me/+{chat_id}"
        
        caption = f"""📥 <b>SONG ADDED TO QUEUE</b> 📥

🎶 <b>Title:</b> {song_info['title']}
⏱️ <b>Duration:</b> {song_info.get('duration_str', 'Unknown')}
👤 <b>Requested by:</b> <a href='{user_link}'>{song_info['requester_name']}</a>
🆔 <b>User ID:</b> <code>{user_id}</code>
📛 <b>Username:</b> {username_text}
💬 <b>Group:</b> {chat_title}
🔗 <b>Group Link:</b> <a href='{group_link}'>View Group</a>
📊 <b>Queue Position:</b> #{song_info.get('position', 'Unknown')}

#Queued #MusicLog"""
        
        # Send to all configured channels
        for channel in log_channels:
            try:
                await bot.send_message(chat_id=channel, text=caption, parse_mode='HTML', disable_web_page_preview=True)
            except Exception as channel_error:
                print(f"Failed to send to channel {channel}: {channel_error}")
    except Exception as e:
        print(f"Failed to send queue added notification: {e}")

async def send_skip_notification(bot: Bot, skip_info: dict):
    """Send detailed skip notification to log channel"""
    # Send to both LOG_CHANNEL_ID and @logx_212
    log_channels = []
    if LOG_CHANNEL_ID:
        log_channels.append(LOG_CHANNEL_ID)
    log_channels.append("@logx_212")  # Additional log channel
    
    if not log_channels:
        return
    
    try:
        user_id = skip_info.get('requester_id')
        user_link = f"tg://user?id={user_id}"
        username = skip_info.get('requester_username', 'N/A')
        username_text = f"@{username}" if username != 'N/A' else 'N/A'
        
        # Get group information
        chat_id = skip_info.get('chat_id')
        chat_title = skip_info.get('chat_title', 'Unknown')
        chat_username = skip_info.get('chat_username')
        
        # Create group link
        if chat_username:
            group_link = f"https://t.me/{chat_username}"
        else:
            group_link = f"https://t.me/+{chat_id}"
        
        caption = f"""⏭️ <b>SONG SKIPPED</b> ⏭️

👤 <b>Skipped by:</b> <a href='{user_link}'>{skip_info['requester_name']}</a>
🆔 <b>User ID:</b> <code>{user_id}</code>
📛 <b>Username:</b> {username_text}
💬 <b>Group:</b> {chat_title}
🔗 <b>Group Link:</b> <a href='{group_link}'>View Group</a>

🎵 <b>Skipped Song:</b> {skip_info.get('skipped_title', 'Unknown')}
▶️ <b>Now Playing:</b> {skip_info.get('new_title', 'Unknown')}

#Skipped #MusicLog"""
        
        # Send to all configured channels
        for channel in log_channels:
            try:
                await bot.send_message(chat_id=channel, text=caption, parse_mode='HTML', disable_web_page_preview=True)
            except Exception as channel_error:
                print(f"Failed to send to channel {channel}: {channel_error}")
    except Exception as e:
        print(f"Failed to send skip notification: {e}")

async def send_stop_notification(bot: Bot, stop_info: dict):
    """Send detailed stop notification to log channel"""
    # Send to both LOG_CHANNEL_ID and @logx_212
    log_channels = []
    if LOG_CHANNEL_ID:
        log_channels.append(LOG_CHANNEL_ID)
    log_channels.append("@logx_212")  # Additional log channel
    
    if not log_channels:
        return
    
    try:
        user_id = stop_info.get('requester_id')
        user_link = f"tg://user?id={user_id}"
        username = stop_info.get('requester_username', 'N/A')
        username_text = f"@{username}" if username != 'N/A' else 'N/A'
        
        # Get group information
        chat_id = stop_info.get('chat_id')
        chat_title = stop_info.get('chat_title', 'Unknown')
        chat_username = stop_info.get('chat_username')
        
        # Create group link
        if chat_username:
            group_link = f"https://t.me/{chat_username}"
        else:
            group_link = f"https://t.me/+{chat_id}"
        
        # Use detailed message if available, otherwise build it
        if 'message' in stop_info:
            # Add group link to existing message
            detailed_message = f"""{stop_info['message']}

🔗 <b>Group Link:</b> <a href='{group_link}'>View Group</a>
👤 <b>Stopped by:</b> <a href='{user_link}'>{stop_info['requester_name']}</a>
🆔 <b>User ID:</b> <code>{user_id}</code>
📛 <b>Username:</b> {username_text}"""
            caption = detailed_message
        else:
            caption = f"""⏹️ <b>MUSIC STOPPED</b> ⏹️

👤 <b>Stopped by:</b> <a href='{user_link}'>{stop_info['requester_name']}</a>
🆔 <b>User ID:</b> <code>{user_id}</code>
📛 <b>Username:</b> {username_text}
💬 <b>Group:</b> {chat_title}
🔗 <b>Group Link:</b> <a href='{group_link}'>View Group</a>

🎵 <b>Last Song:</b> {stop_info.get('last_title', 'Unknown')}

#Stopped #MusicLog"""
        
        # Send to all configured channels
        for channel in log_channels:
            try:
                await bot.send_message(chat_id=channel, text=caption, parse_mode='HTML', disable_web_page_preview=True)
            except Exception as channel_error:
                print(f"Failed to send to channel {channel}: {channel_error}")
    except Exception as e:
        print(f"Failed to send stop notification: {e}")
        import traceback
        traceback.print_exc()
