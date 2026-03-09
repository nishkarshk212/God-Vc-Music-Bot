import os
import asyncio
from pytgcalls.types.stream import MediaStream
from pytgcalls.types.stream import AudioQuality

active_chats = {}
vc_monitor_tasks = {}  # Track monitoring tasks per chat
current_playing = {}  # Store current playing item info for seek support

def get_current_playing(chat_id):
    """Get currently playing song for a chat"""
    return current_playing.get(chat_id)

def is_playing(chat_id):
    return chat_id in active_chats

async def start_playback(chat_id, is_video=False):
    """Start playback for a chat"""
    from core.queue import pop_song
    from bot import call_py
    
    print(f"\n🔍 Attempting to start {'VIDEO' if is_video else 'AUDIO'} playback in chat {chat_id}")
    
    if not is_playing(chat_id):
        next_item = pop_song(chat_id)
        if next_item:
            is_video = next_item.get("is_video", False)
            print(f"🎵 Got next item from queue: {next_item['title']} (Video: {is_video})")
            url = next_item["url"]
            print(f"🔗 URL: {url[:80]}...")
            
            # Check if it's a local file and verify it exists and is not empty
            if not url.startswith(("http://", "https://")):
                if not os.path.exists(url) or os.path.getsize(url) < 10000:
                    print(f"❌ ERROR: Local file {url} is missing, too small, or corrupted!")
                    # Try to search again or notify user
                    raise Exception(f"Video/Audio file corrupted or missing: {url}")

            # Store current item for seek support
            current_playing[chat_id] = next_item

            try:
                # Unified ffmpeg parameters for both audio and video to ensure consistent sound
                # Adding specific audio filters that fixed the "no sound" issue in video
                is_url = url.startswith(("http://", "https://"))
                ffmpeg_args = (
                    "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 10 " if is_url else ""
                )
                ffmpeg_args += (
                    "-af \"volume=2.0,loudnorm=I=-16:TP=-1.5:LRA=11\" "
                    "-ac 2 -ar 48000 -acodec pcm_s16le"
                )
                
                if is_video:
                    # Video specific parameters
                    from pytgcalls.types.stream import VideoQuality
                    stream = MediaStream(
                        url,
                        audio_parameters=AudioQuality.STUDIO,
                        video_parameters=VideoQuality.HD_720P,
                        ffmpeg_parameters=ffmpeg_args
                    )
                else:
                    # Audio only - Use the same robust parameters as video
                    stream = MediaStream(
                        url,
                        audio_parameters=AudioQuality.STUDIO,
                        ffmpeg_parameters=ffmpeg_args
                    )
                
                print(f"📞 Starting playback with MediaStream ({'VIDEO' if is_video else 'AUDIO'})")
                await call_py.play(chat_id, stream)
                
                # Small delay to ensure initialization before unmuting
                await asyncio.sleep(1.5)
                
                # Force unmute using both PyTgCalls methods for maximum reliability
                try:
                    await call_py.unmute(chat_id)
                except Exception:
                    pass
                    
                active_chats[chat_id] = True
                print(f"✅ SUCCESS: Started playing: {next_item['title']} in chat {chat_id}")
                
                # Start VC monitor to auto-stop if empty
                await start_vc_monitor(chat_id)
            except Exception as e:
                print(f"❌ ERROR starting playback: {type(e).__name__}: {e}")
                
                # Fallback to direct URL with standard quality
                try:
                    print(f"🔄 Falling back to direct URL play...")
                    await call_py.play(chat_id, url)
                    active_chats[chat_id] = True
                except Exception:
                    # Silent failure - just put back in queue or move on
                    from core.queue import music_queue
                    if chat_id not in music_queue:
                        music_queue[chat_id] = []
                    music_queue[chat_id].insert(0, next_item)
                    # We no longer raise the exception to avoid sending error messages to group
        else:
            print(f"⚠️ No item in queue for chat {chat_id}")
    else:
        print(f"⏸️ Already playing in chat {chat_id}")

async def start_playback_video(chat_id):
    # Pass is_video=True to start_playback
    await start_playback(chat_id, is_video=True)

async def change_stream(chat_id, stream_url):
    """Change the stream for a chat (used during skip)"""
    from bot import call_py
    
    # Use the same robust parameters that work for video
    is_url = stream_url.startswith(("http://", "https://"))
    ffmpeg_args = (
        "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 10 " if is_url else ""
    )
    ffmpeg_args += (
        "-af \"volume=2.0,loudnorm=I=-16:TP=-1.5:LRA=11\" "
        "-ac 2 -ar 48000 -acodec pcm_s16le"
    )
    
    stream = MediaStream(
        stream_url,
        audio_parameters=AudioQuality.STUDIO,
        ffmpeg_parameters=ffmpeg_args
    )
    await call_py.play(chat_id, stream)
    
    # Force unmute after stream change (fixes no sound after skip)
    await asyncio.sleep(1.5)
    try:
        await call_py.unmute(chat_id)
        print(f"✅ Unmuted after stream change in chat {chat_id}")
    except Exception as e:
        print(f"⚠️ Failed to unmute: {e}")

async def pause(chat_id):
    await call_py.pause_stream(chat_id)

async def resume(chat_id):
    await call_py.resume_stream(chat_id)

async def seek(chat_id, seconds):
    """Seek to a specific time in the current stream"""
    item = current_playing.get(chat_id)
    if not item:
        return False
    
    url = item.get("url")
    is_video = item.get("is_video", False)
    
    try:
        # For local files, we use -ss offset in ffmpeg_parameters
        ffmpeg_args = f"-ss {seconds} "
        
        if is_video:
            from pytgcalls.types.stream import VideoQuality
            stream = MediaStream(
                url,
                audio_parameters=AudioQuality.STUDIO,
                video_parameters=VideoQuality.HD_720P,
                ffmpeg_parameters=ffmpeg_args
            )
        else:
            stream = MediaStream(
                url,
                audio_parameters=AudioQuality.STUDIO,
                ffmpeg_parameters=ffmpeg_args
            )
        
        await call_py.play(chat_id, stream)
        # Force unmute after seek
        await asyncio.sleep(1)
        await call_py.unmute(chat_id)
        return True
    except Exception as e:
        print(f"Seek error: {e}")
        return False

async def stop(chat_id):
    """Stop playback and clear queue"""
    from core.queue import queue_manager
    from bot import call_py
    
    # Stop VC monitor if running
    stop_vc_monitor(chat_id)
    
    # Mark VC as ended and clear queue
    from core.queue import queue_manager
    queue_manager.mark_vc_ended(chat_id)
    
    try:
        await call_py.leave_call(chat_id)
    except Exception as e:
        # If already left or error, just ensure active_chats is updated
        print(f"Error leaving call: {e}")
        
    active_chats.pop(chat_id, None)
    current_playing.pop(chat_id, None)
    print(f"⏹️ Playback stopped and queue cleared for chat {chat_id}")

async def change_stream_video(chat_id, stream_url):
    """Change the video stream for a chat (used during skip)"""
    from bot import call_py
    from pytgcalls.types.stream import VideoQuality
    
    # Use STUDIO quality and HD_720P for video stream changes
    is_url = stream_url.startswith(("http://", "https://"))
    ffmpeg_args = (
        "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 10 " if is_url else ""
    )
    ffmpeg_args += (
        "-af \"volume=2.0,loudnorm=I=-16:TP=-1.5:LRA=11\" "
        "-ac 2 -ar 48000 -acodec pcm_s16le"
    )
    
    stream = MediaStream(
        stream_url,
        audio_parameters=AudioQuality.STUDIO,
        video_parameters=VideoQuality.HD_720P,
        ffmpeg_parameters=ffmpeg_args
    )
    await call_py.play(chat_id, stream)
    
    # Force unmute after stream change (fixes no sound after skip)
    await asyncio.sleep(1.5)
    try:
        await call_py.unmute(chat_id)
        print(f"✅ Unmuted after video stream change in chat {chat_id}")
    except Exception as e:
        print(f"⚠️ Failed to unmute: {e}")

async def skip_next(chat_id):
    # Stop VC monitor before skipping
    stop_vc_monitor(chat_id)
    
    next_item = pop_song(chat_id)
    if next_item:
        url = next_item.get("url")
        is_video = next_item.get("is_video", False)
        title = next_item.get("title", "Unknown")
        
        print(f"⏭️ Skipping to next item: {title} (Video: {is_video})")
        
        # Check if it's a local file and verify it exists
        if url and not url.startswith(("http://", "https://")):
            if not os.path.exists(url):
                print(f"❌ ERROR: Local file {url} for '{title}' is missing!")
                # If file is missing, try skipping again to the next one
                return await skip_next(chat_id)
        
        # Store current item for seek support
        current_playing[chat_id] = next_item
        
        try:
            if is_video:
                await change_stream_video(chat_id, url)
            else:
                await change_stream(chat_id, url)
            
            # Restart monitor for new song
            await start_vc_monitor(chat_id)
            print(f"✅ Successfully skipped to: {title}")
        except Exception as e:
            print(f"❌ Error during skip playback: {e}")
            # If playback fails, try the next one
            return await skip_next(chat_id)
    else:
        print(f"⏹️ No more items in queue for chat {chat_id}. Stopping playback.")
        await stop(chat_id)

async def start_vc_monitor(chat_id):
    """Start monitoring voice chat for participants - auto-stop if empty for 30 seconds"""
    print(f"🔍 Starting VC monitor for chat {chat_id}")
    
    # Cancel existing monitor if any
    stop_vc_monitor(chat_id)
    
    # Create new monitor task
    vc_monitor_tasks[chat_id] = asyncio.create_task(vc_participant_monitor(chat_id))
    print(f"✅ VC monitor started for chat {chat_id}")

def stop_vc_monitor(chat_id):
    """Stop the VC monitor for a specific chat"""
    if chat_id in vc_monitor_tasks:
        vc_monitor_tasks[chat_id].cancel()
        del vc_monitor_tasks[chat_id]
        print(f"⏹️ VC monitor stopped for chat {chat_id}")

async def vc_participant_monitor(chat_id):
    """Monitor voice chat participants and auto-stop if empty for 30 seconds"""
    try:
        empty_count = 0
        max_empty_checks = 6  # Check every 5 seconds, stop after 30 seconds (6 * 5 = 30)
        
        while True:
            await asyncio.sleep(5)  # Check every 5 seconds
            
            # Get current participants
            try:
                from bot import call_py
                participants = await call_py.get_participants(chat_id)
                participant_count = len(participants) if participants else 0
                
                print(f"👥 VC Monitor - Chat {chat_id}: {participant_count} participants")
                
                if participant_count == 0:
                    empty_count += 1
                    print(f"⚠️ VC is empty! Count: {empty_count}/{max_empty_checks}")
                    
                    if empty_count >= max_empty_checks:
                        # VC has been empty for 30 seconds - auto-stop
                        print(f"⏹️ Auto-stopping stream - VC empty for 30 seconds")
                        
                        # Send notification to log channel
                        try:
                            from aiogram import Bot
                            from config import BOT_TOKEN
                            bot = Bot(token=BOT_TOKEN)
                            
                            from utils.logger import send_stop_notification
                            stop_info = {
                                "requester_name": "Auto-Stop",
                                "requester_id": 0,
                                "requester_username": "N/A",
                                "chat_id": chat_id,
                                "chat_title": f"Voice Chat (Empty)",
                                "chat_username": None,
                                "last_title": "Stream ended - No participants",
                                "message": f"⏹️ <b>AUTO-STOPPED</b>\n\n💬 Voice chat was empty for 30 seconds.\n🗑️ Queue cleared automatically.\n🎵 Stream stopped.\n\n#AutoStop"
                            }
                            asyncio.create_task(send_stop_notification(bot=bot, stop_info=stop_info))
                        except Exception as notify_err:
                            print(f"Failed to send auto-stop notification: {notify_err}")
                        
                        # Stop the stream and clear queue
                        await stop(chat_id)
                        print(f"✅ Stream auto-stopped and queue cleared successfully")
                        break
                else:
                    # Reset counter if someone joins
                    empty_count = 0
                    
            except Exception as check_err:
                print(f"❌ Error checking participants: {check_err}")
                # If we can't check (e.g., bot left VC), stop monitoring
                break
                
    except asyncio.CancelledError:
        print(f"✅ VC monitor cancelled for chat {chat_id}")
    except Exception as e:
        print(f"❌ VC monitor error: {e}")
