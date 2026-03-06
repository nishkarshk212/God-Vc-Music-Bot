from collections import defaultdict

music_queue = defaultdict(list)

def add_to_queue(chat_id, item):
    music_queue[chat_id].append(item)

def get_queue(chat_id):
    return list(music_queue[chat_id])

def pop_song(chat_id):
    if music_queue[chat_id]:
        return music_queue[chat_id].pop(0)

def clear_queue(chat_id):
    music_queue[chat_id].clear()
