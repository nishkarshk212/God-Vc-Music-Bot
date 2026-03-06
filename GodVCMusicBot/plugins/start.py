from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

router = Router()

@router.message(Command("start"))
async def start(message: types.Message):
    msg = await message.reply("⚡ Booting Music System...")
    frames = [
        "⚡ Booting Music System...\n\n▰▱▱▱▱",
        "⚡ Booting Music System...\n\n▰▰▱▱▱",
        "⚡ Booting Music System...\n\n▰▰▰▱▱",
        "⚡ Booting Music System...\n\n▰▰▰▰▱",
        "⚡ Booting Music System...\n\n▰▰▰▰▰",
        "🎧 Loading Music Engine...",
        "🎶 Preparing Interface...",
    ]
    for frame in frames:
        await asyncio.sleep(0.7)
        try:
            await msg.edit_text(frame)
        except Exception:
            await asyncio.sleep(1.0)
            try:
                await msg.edit_text(frame)
            except Exception:
                pass
    bot_info = await message.bot.get_me()
    bot_un = bot_info.username or "yourbot"
    bot_name = bot_info.first_name or "Music Bot"
    user_name = message.from_user.first_name if message.from_user else "User"
    final_text = (
        f"нєу {user_name}, 🥀\n\n"
        f"๏ ᴛʜɪs ɪs ❛ {bot_name}❜ !\n\n"
        "➻ ᴀ ғᴀsᴛ & ᴘᴏᴡᴇʀғᴜʟ ᴛᴇʟᴇɢʀᴀᴍ ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ ʙᴏᴛ ᴡɪᴛʜ sᴏᴍᴇ ᴀᴡᴇsᴏᴍᴇ ғᴇᴀᴛᴜʀᴇs.\n\n"
        "──────────────────\n"
        "๏ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʜᴇʟᴩ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴍʏ ᴍᴏᴅᴜʟᴇs ᴀɴᴅ ᴄᴏᴍᴍᴀɴᴅs."
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="𝑨̲̅𝒅̲̅𝒅̲̅ 𝑴̲̅𝒆̲̅ 𝑩̲̅𝒂̲̅𝒃̲̅𝒚̲̅🥀", url=f"https://t.me/{bot_un}?startgroup=true")],
        [InlineKeyboardButton(text="ʜᴇʟᴘ✦", callback_data="help"), InlineKeyboardButton(text="𝕆𝕨𝕟𝕖𝕣♛", url="https://t.me/Jayden_212")],
        [InlineKeyboardButton(text="𝑼̲̅𝒑̲̅𝒅̲̅𝒂̲̅𝒕̲̅𝒆̲̅𝒔̲̅⛲︎", url="https://t.me/Tele_212_bots")]
    ])
    try:
        await msg.edit_text(final_text, reply_markup=keyboard)
    except Exception:
        await message.answer(final_text, reply_markup=keyboard)

@router.callback_query()
async def start_callbacks(callback_query: types.CallbackQuery):
    if callback_query.data == "close":
        await callback_query.message.delete()
    elif callback_query.data == "commands":
        await callback_query.message.edit_text(
            "🎵 **Music Commands**\n\n/play - play music\n/pause - pause music\n/resume - resume music\n/skip - skip song\n/stop - stop music\n/queue - show queue",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Back", callback_data="home")]]),
        )
    elif callback_query.data == "help":
        await callback_query.message.edit_text(
            "📚 **How To Use**\n\n1️⃣ Add bot to group\n2️⃣ Start voice chat\n3️⃣ Use /play song name\n\nBot will stream music in VC.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Commands", callback_data="commands")], 
                [InlineKeyboardButton(text="🔙 Back", callback_data="home")]
            ]),
        )
    elif callback_query.data == "home":
        bot_info = await callback_query.bot.get_me()
        bot_un = bot_info.username or "yourbot"
        bot_name = bot_info.first_name or "Music Bot"
        user_name = callback_query.from_user.first_name if callback_query.from_user else "User"
        final_text = (
            f"нєу {user_name}, 🥀\n\n"
            f"๏ ᴛʜɪs ɪs ❛ {bot_name}❜ !\n\n"
            "➻ ᴀ ғᴀsᴛ & ᴘᴏᴡᴇʀғᴜʟ ᴛᴇʟᴇɢʀᴀᴍ ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ ʙᴏᴛ ᴡɪᴛʜ sᴏᴍᴇ ᴀᴡᴇsᴏᴍᴇ ғᴇᴀᴛᴜʀᴇs.\n\n"
            "──────────────────\n"
            "๏ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʜᴇʟᴩ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴍʏ ᴍᴏᴅᴜʟᴇs ᴀɴᴅ ᴄᴏᴍᴍᴀɴᴅs."
        )
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="𝑨̲̅𝒅̲̅𝒅̲̅ 𝑴̲̅𝒆̲̅ 𝑩̲̅𝒂̲̅𝒃̲̅𝒚̲̅🥀", url=f"https://t.me/{bot_un}?startgroup=true")],
            [InlineKeyboardButton(text="ʜᴇʟᴘ✦", callback_data="help")]
        ])
        await callback_query.message.edit_text(final_text, reply_markup=keyboard)
