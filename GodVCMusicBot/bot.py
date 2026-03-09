from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import API_ID, API_HASH, BOT_TOKEN, LOG_CHANNEL_ID, SESSION_STRING
import asyncio
from pathlib import Path
import sys
import logging
import nest_asyncio
import traceback
from hydrogram import Client
from pytgcalls import PyTgCalls

# Allow nested event loops (required for PyTgCalls + aiogram)
nest_asyncio.apply()

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Initialize the assistant (user bot)
assistant = Client(
    "assistant",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING,
)

# Initialize PyTgCalls
call_py = PyTgCalls(assistant)

# Setup logging to send to Telegram channel
from utils.logger import setup_logging
setup_logging(bot)

print("📦 Loading plugins...")
# Import all plugin handlers
from plugins import start, play, vplay, ping, stop, skip, player_controls, queue_cmd, promo, settings

# Include routers in dispatcher
dp.include_router(start.router)
dp.include_router(play.router)
dp.include_router(vplay.router)
dp.include_router(ping.router)
dp.include_router(stop.router)
dp.include_router(skip.router)
dp.include_router(player_controls.router)
dp.include_router(queue_cmd.router)
dp.include_router(promo.router)
dp.include_router(settings.router)

print("✅ Plugins loaded\n")

async def main():
    """Initializes and runs the bot."""
    print("\n🔄 Starting bot components...")

    # Start the assistant and PyTgCalls
    print("📞 Starting assistant...")
    await assistant.start()
    print("✅ Assistant started.")

    print("🎵 Starting PyTgCalls...")
    await call_py.start()
    print("✅ PyTgCalls started.")

    # Get and print bot info
    bot_info = await bot.get_me()
    print(f"\n{'='*50}")
    print(f"✅ Bot started successfully!")
    print(f"🤖 Name: {bot_info.first_name}")
    print(f"🆔 ID: {bot_info.id}")
    print(f"📛 Username: @{bot_info.username}")
    print(f"{'='*50}\n")
    print("🎵 Bot is ready! Send /play <song> to test.\n")

    try:
        await dp.start_polling(bot)
    finally:
        print("\n🔄 Stopping bot...")
        await bot.session.close()
        await call_py.stop()
        await assistant.stop()
        print("✅ Bot stopped cleanly.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\n👋 Bot stopped by user.")
