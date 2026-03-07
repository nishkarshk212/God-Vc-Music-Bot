from assistant import call_py, assistant
from core.queue import pop_song

active_chats = {}

def is_playing(chat_id):
    return chat_id in active_chats

async def start_playback(chat_id):
    print(f"\n🔍 Attempting to start playback in chat {chat_id}")
    print(f"📊 Is playing check: {is_playing(chat_id)}")
    
    if not is_playing(chat_id):
        next_item = pop_song(chat_id)
        if next_item:
            print(f"🎵 Got next item from queue: {next_item['title']}")
            print(f"🔗 URL: {next_item['url'][:80]}...")
            try:
                print(f"📞 Calling call_py.play({chat_id}, ...)")
                await call_py.play(chat_id, next_item["url"])
                active_chats[chat_id] = True
                print(f"✅ SUCCESS: Started playing: {next_item['title']} in chat {chat_id}")
            except Exception as e:
                print(f"❌ ERROR starting playback: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
                
                # Put the song back in queue at the front
                from core.queue import music_queue
                music_queue[chat_id].insert(0, next_item)
                
                raise
        else:
            print(f"⚠️ No item in queue for chat {chat_id}")
    else:
        print(f"⏸️ Already playing in chat {chat_id}")

async def start_playback_video(chat_id):
    if not is_playing(chat_id):
        next_item = pop_song(chat_id)
        if next_item:
            try:
                await call_py.play(chat_id, next_item["url"], video=True)
                active_chats[chat_id] = True
                print(f"✅ Started playing video: {next_item['title']} in chat {chat_id}")
            except Exception as e:
                print(f"❌ Error starting video playback: {e}")
                raise

async def change_stream(chat_id, stream_url):
    await call_py.play(chat_id, stream_url)

async def change_stream_video(chat_id, stream_url):
    await call_py.play(chat_id, stream_url, video=True)

async def pause(chat_id):
    await call_py.pause(chat_id)

async def resume(chat_id):
    await call_py.resume(chat_id)

async def stop(chat_id):
    try:
        await call_py.leave_call(chat_id)
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
