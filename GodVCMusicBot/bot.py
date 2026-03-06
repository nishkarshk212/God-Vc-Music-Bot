from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import API_ID, API_HASH, BOT_TOKEN, LOG_CHANNEL_ID
import asyncio
from pathlib import Path
import sys
import logging
import nest_asyncio
import traceback

# Allow nested event loops (required for PyTgCalls + aiogram)
nest_asyncio.apply()

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Setup logging to send to Telegram channel
from utils.logger import setup_logging
setup_logging(bot)

print("📦 Loading plugins...")
# Import all plugin handlers
from GodVCMusicBot.plugins import start, play, vplay, ping, stop, skip, player_controls, queue_cmd, promo, settings

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

if __name__ == "__main__":
    async def on_startup(dispatcher):
        """Called when bot starts"""
        print("\n🔄 Starting bot components...")
        
        # Import assistant here (after event loop is created)
        from assistant import assistant, call_py
        
        # Start assistant and PyTgCalls FIRST (before aiogram polling)
        print("📞 Starting assistant...")
        await assistant.start()
        print("✅ Assistant started")
        
        print("🎵 Starting PyTgCalls...")
        await call_py.start()
        print("✅ PyTgCalls started")
        
        # Initialize auto-maintenance system
        from utils.auto_maintenance import init_maintenance, start_maintenance
        maintenance_instance = init_maintenance(bot)
        
        bot_info = await bot.get_me()
        print(f"\n{'='*50}")
        print(f"✅ Bot started successfully!")
        print(f"🤖 Name: {bot_info.first_name}")
        print(f"🆔 ID: {bot_info.id}")
        print(f"📛 Username: @{bot_info.username}")
        print(f"{'='*50}\n")
        print("🎵 Bot is ready! Send /play <song> to test.\n")
        
        # Start auto-maintenance loop in background
        print("🔧 Starting auto-maintenance system...")
        asyncio.create_task(start_maintenance())
        print("✅ Auto-maintenance activated\n")
    
    async def on_shutdown(dispatcher):
        """Called when bot stops"""
        print("\n🔄 Stopping bot...")
        from assistant import assistant, call_py
        
        await bot.session.close()
        try:
            await assistant.stop()
            call_py.stop()
        except:
            pass
        print("✅ Bot stopped cleanly")
    
    # Register startup/shutdown handlers
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Run polling with crash recovery
    async def run_with_recovery():
        """Run bot with automatic crash recovery"""
        while True:
            try:
                await dp.start_polling(bot)
                break  # If polling stops normally, exit loop
            except Exception as e:
                print(f"\n{'='*50}")
                print(f"❌ BOT CRASH DETECTED!")
                print(f"Error: {type(e).__name__}: {str(e)}")
                print(f"{'='*50}\n")
                
                # Log crash to channel
                try:
                    error_details = traceback.format_exc()
                    crash_msg = f"""
🚨 <b>CRASH RECOVERY ACTIVATED</b> 🚨

❌ <b>Error:</b> <code>{type(e).__name__}</code>
📝 <b>Details:</b> <code>{str(e)}</code>

<b>Stack Trace:</b>
<code>{error_details[:3000]}</code>

🔧 Attempting automatic recovery...
"""
                    await bot.send_message(
                        chat_id=LOG_CHANNEL_ID,
                        text=crash_msg,
                        parse_mode='HTML'
                    )
                except:
                    pass
                
                # Perform crash recovery
                from utils.auto_maintenance import init_maintenance
                maintenance_instance = init_maintenance(bot)
                if maintenance_instance:
                    await maintenance_instance.crash_recovery(e)
                
                # Wait a moment before restarting
                print("⏳ Waiting 5 seconds before restart...")
                await asyncio.sleep(5)
                
                # Try to restart polling
                print("🔄 Restarting bot polling...\n")
    
    # Run the bot with crash recovery
    try:
        asyncio.run(run_with_recovery())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
