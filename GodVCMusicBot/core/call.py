import os
from assistant import call_py, assistant
from core.queue import pop_song
from pytgcalls.types.stream import MediaStream
from pytgcalls.types.stream import AudioQuality

active_chats = {}

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
    try:
        await call_py.leave_group_call(chat_id)
    except Exception as e:
        print(f"Error leaving call: {e}")
    active_chats.pop(chat_id, None)

async def skip_next(chat_id):
    next_item = pop_song(chat_id)
    if next_item:
        if next_item.get("is_video"):
            await change_stream_video(chat_id, next_item["url"])
        else:
            await change_stream(chat_id, next_item["url"])
