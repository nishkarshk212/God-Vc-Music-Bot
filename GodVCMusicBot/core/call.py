import os
import asyncio
from assistant import call_py, assistant
from core.queue import pop_song, get_queue, clear_queue
from pytgcalls.types.stream import MediaStream
from pytgcalls.types.stream import AudioQuality

active_chats = {}
vc_monitor_tasks = {}  # Track monitoring tasks per chat

def is_playing(chat_id):
    return chat_id in active_chats

async def start_playback(chat_id):
    print(f"\n🔍 Attempting to start playback in chat {chat_id}")
    
    if not is_playing(chat_id):
        next_item = pop_song(chat_id)
        if next_item:
            print(f"🎵 Got next item from queue: {next_item['title']}")
            url = next_item["url"]
            print(f"🔗 URL: {url[:80]}...")
            
            try:
                # Use MediaStream for PyTgCalls 2.x with ENHANCED audio quality settings
                stream = MediaStream(
                    url,
                    audio_parameters=AudioQuality.STUDIO,  # Highest quality (320kbps)
                    additional_ffmpeg_parameters=[
                        "-reconnect", "1",
                        "-reconnect_streamed", "1",
                        "-reconnect_delay_max", "10",  # Increased from 5 to 10
                        "-bufsize", "256k",  # Increased buffer for smoother playback
                        "-max_delay", "1000000",  # Increased max delay
                        "-fflags", "+genpts",  # Generate presentation timestamps
                        "-flags", "+low_delay",  # Low delay flag
                        "-strict", "normal",  # Strict normal for better compatibility
                        "-ar", "48000",  # Audio sample rate 48kHz (better quality)
                        "-ac", "2",  # Stereo audio
                        "-b:a", "320k",  # Maximum audio bitrate
                        "-preset", "ultrafast",  # Fast encoding to prevent buffering
                        "-probesize", "10000000",  # Larger probe size for better stream detection
                        "-analyzeduration", "5000000",  # Longer analysis duration
                    ]
                )
                
                print(f"📞 Starting playback with MediaStream (ENHANCED QUALITY)")
                await call_py.play(chat_id, stream)
                active_chats[chat_id] = True
                print(f"✅ SUCCESS: Started playing: {next_item['title']} in chat {chat_id}")
                
                # Start VC monitor to auto-stop if empty
                await start_vc_monitor(chat_id)
            except Exception as e:
                print(f"❌ ERROR starting playback: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
                
                # Fallback to direct URL with standard quality
                try:
                    print(f"🔄 Falling back to direct URL play...")
                    await call_py.play(chat_id, url)
                    active_chats[chat_id] = True
                except Exception as e2:
                    print(f"❌ Fallback also failed: {e2}")
                    # Put back in queue
                    from core.queue import music_queue
                    if chat_id not in music_queue:
                        music_queue[chat_id] = []
                    music_queue[chat_id].insert(0, next_item)
                    raise Exception(f"Voice Chat Playback Failed: {str(e)}")
        else:
            print(f"⚠️ No item in queue for chat {chat_id}")
    else:
        print(f"⏸️ Already playing in chat {chat_id}")

async def start_playback_video(chat_id):
    # For now, focus on audio as requested for compatibility
    await start_playback(chat_id)

async def change_stream(chat_id, stream_url):
    # Use STUDIO quality for stream changes too
    stream = MediaStream(
        stream_url,
        audio_parameters=AudioQuality.STUDIO,
        additional_ffmpeg_parameters=[
            "-reconnect", "1",
            "-reconnect_streamed", "1",
            "-reconnect_delay_max", "10",
            "-bufsize", "256k",
            "-max_delay", "1000000",
            "-fflags", "+genpts",
            "-flags", "+low_delay",
            "-strict", "normal",
            "-ar", "48000",
            "-ac", "2",
            "-b:a", "320k",
            "-preset", "ultrafast",
            "-probesize", "10000000",
            "-analyzeduration", "5000000",
        ]
    )
    await call_py.play(chat_id, stream)

async def pause(chat_id):
    await call_py.pause_stream(chat_id)

async def resume(chat_id):
    await call_py.resume_stream(chat_id)

async def stop(chat_id):
    # Stop VC monitor if running
    stop_vc_monitor(chat_id)
    
    try:
        await call_py.leave_group_call(chat_id)
    except Exception as e:
        print(f"Error leaving call: {e}")
    active_chats.pop(chat_id, None)

async def skip_next(chat_id):
    # Stop VC monitor before skipping
    stop_vc_monitor(chat_id)
    
    next_item = pop_song(chat_id)
    if next_item:
        if next_item.get("is_video"):
            await change_stream_video(chat_id, next_item["url"])
        else:
            await change_stream(chat_id, next_item["url"])
        
        # Restart monitor for new song
        await start_vc_monitor(chat_id)

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
                from assistant import call_py
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
                                "message": f"⏹️ <b>AUTO-STOPPED</b>\n\n💬 Voice chat was empty for 30 seconds.\n🎵 Stream stopped automatically.\n\n#AutoStop"
                            }
                            asyncio.create_task(send_stop_notification(bot=bot, stop_info=stop_info))
                        except Exception as notify_err:
                            print(f"Failed to send auto-stop notification: {notify_err}")
                        
                        # Stop the stream
                        await stop(chat_id)
                        print(f"✅ Stream auto-stopped successfully")
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
