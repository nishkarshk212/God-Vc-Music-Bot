from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def format_progress(current, total):
    if total <= 0:
        return "0%"
    pct = int((current / total) * 100)
    return f"{pct}%"

def progress_bar(current, total):
    if total <= 0:
        total = 1
    if current < 0:
        current = 0
    if current > total:
        current = total
    bar_length = 20
    filled = int(bar_length * current / total)
    if filled >= bar_length:
        filled = bar_length - 1
    bar = ("━" * filled) + "●" + ("─" * (bar_length - filled - 1))
    return f"{current} {bar} {total}"

def format_duration(seconds):
    if seconds is None:
        return "Unknown"
    try:
        seconds = int(seconds)
    except Exception:
        return str(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"

def time_formatter(seconds: int):
    minutes, seconds = divmod(int(seconds), 60)
    return f"{minutes}:{seconds:02d}"

def progress_line(current, total, length=12):
    if total <= 0:
        total = 1
    current = max(0, min(current, total))
    filled = int(length * current / total)
    empty = max(0, length - filled)
    return ("─" * filled) + "●" + ("─" * empty)

def build_keyboard(current, duration):
    slider_text = f"⏱ {time_formatter(current)} {progress_line(current, duration)} {time_formatter(duration)}"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=slider_text, callback_data="slider")],
            [InlineKeyboardButton(text="=", callback_data="pause"), InlineKeyboardButton(text="➣", callback_data="resume"), InlineKeyboardButton(text="❏", callback_data="stop")],
            [InlineKeyboardButton(text="↺", callback_data="seek_back_5"), InlineKeyboardButton(text="↻", callback_data="seek_fwd_5")],
            [InlineKeyboardButton(text="✖︎", callback_data="close")],
        ]
    )

async def update_slider(client, chat_id, msg_id, duration):
    current = 0
    while current <= int(duration):
        try:
            await client.edit_message_reply_markup(chat_id, msg_id, reply_markup=build_keyboard(current, duration))
        except Exception:
            pass
        await __import__("asyncio").sleep(5)
        current += 5

SLIDERS = {}

def _k(chat_id, msg_id):
    return f"{chat_id}:{msg_id}"

async def start_slider(client, chat_id, msg_id, duration, prefix=""):
    SLIDERS[_k(chat_id, msg_id)] = {
        "current": 0,
        "duration": int(duration),
        "paused": False,
        "stopped": False,
        "prefix": prefix or "🎵 **Now Playing**",
    }
    while True:
        state = SLIDERS.get(_k(chat_id, msg_id))
        if not state or state.get("stopped"):
            break
        if state.get("paused"):
            await __import__("asyncio").sleep(1)
            continue
        cur = state["current"]
        dur = state["duration"]
        if cur > dur:
            break
        
        # Build updated caption with progress
        keyboard = build_keyboard(cur, dur)
        
        try:
            # Update both caption and keyboard
            await client.edit_message_caption(
                chat_id=chat_id,
                message_id=msg_id,
                caption=state["prefix"],
                reply_markup=keyboard
            )
        except Exception as e:
            # If caption edit fails, try just keyboard
            try:
                await client.edit_message_reply_markup(chat_id, msg_id, reply_markup=keyboard)
            except Exception:
                pass
        
        await __import__("asyncio").sleep(5)
        state["current"] = min(dur, cur + 5)

def pause_slider(chat_id, msg_id):
    state = SLIDERS.get(_k(chat_id, msg_id))
    if state:
        state["paused"] = True

def resume_slider(chat_id, msg_id):
    state = SLIDERS.get(_k(chat_id, msg_id))
    if state:
        state["paused"] = False

def stop_slider(chat_id, msg_id):
    state = SLIDERS.get(_k(chat_id, msg_id))
    if state:
        state["stopped"] = True

def seek_slider(chat_id, msg_id, delta_seconds):
    state = SLIDERS.get(_k(chat_id, msg_id))
    if state:
        cur = state["current"] + int(delta_seconds)
        cur = max(0, min(cur, state["duration"]))
        state["current"] = cur

def reset_slider(chat_id, msg_id):
    state = SLIDERS.get(_k(chat_id, msg_id))
    if state:
        state["current"] = 0
