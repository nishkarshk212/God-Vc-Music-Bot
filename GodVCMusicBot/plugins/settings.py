from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.settings import get_chat_settings, update_chat_setting, reset_chat_settings

router = Router()


def build_settings_keyboard(chat_id: int) -> InlineKeyboardMarkup:
    """Build settings keyboard with current values"""
    settings = get_chat_settings(chat_id)
    
    # Icons for modes
    mode_icons = {
        "everyone": "🌐",
        "admin_only": "👤",
        "requester_only": "🎯"
    }
    
    keyboard = [
        # Play Mode Row
        [
            InlineKeyboardButton(
                text=f"{mode_icons.get(settings['play_mode'], '🌐')} Play Mode: {settings['play_mode'].replace('_', ' ').title()}",
                callback_data="set_play_mode"
            )
        ],
        # Skip Mode Row
        [
            InlineKeyboardButton(
                text=f"{mode_icons.get(settings['skip_mode'], '🌐')} Skip Mode: {settings['skip_mode'].replace('_', ' ').title()}",
                callback_data="set_skip_mode"
            )
        ],
        # Stop Mode Row
        [
            InlineKeyboardButton(
                text=f"{mode_icons.get(settings['stop_mode'], '🌐')} Stop Mode: {settings['stop_mode'].replace('_', ' ').title()}",
                callback_data="set_stop_mode"
            )
        ],
        # Queue Limit Row
        [
            InlineKeyboardButton(
                text=f"📊 Queue Limit: {'Unlimited' if settings['queue_limit'] == 0 else settings['queue_limit']}",
                callback_data="set_queue_limit"
            )
        ],
        # Auto Skip Row
        [
            InlineKeyboardButton(
                text=f"{'✅' if settings['auto_skip'] else '❌'} Auto Skip: {'ON' if settings['auto_skip'] else 'OFF'}",
                callback_data="toggle_auto_skip"
            )
        ],
        # Log Actions Row
        [
            InlineKeyboardButton(
                text=f"{'📢' if settings['log_actions'] else '🔇'} Log Actions: {'ON' if settings['log_actions'] else 'OFF'}",
                callback_data="toggle_log_actions"
            )
        ],
        # Reset & Close Row
        [
            InlineKeyboardButton(text="🔄 Reset to Default", callback_data="reset_settings"),
            InlineKeyboardButton(text="✕ Close", callback_data="close")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def build_mode_selection_keyboard(setting_type: str) -> InlineKeyboardMarkup:
    """Build keyboard for mode selection"""
    keyboard = [
        [
            InlineKeyboardButton(text="🌐 Everyone", callback_data=f"mode_{setting_type}_everyone"),
            InlineKeyboardButton(text="👤 Admin Only", callback_data=f"mode_{setting_type}_admin_only"),
        ],
        [
            InlineKeyboardButton(text="🎯 Requester Only", callback_data=f"mode_{setting_type}_requester_only"),
        ],
        [
            InlineKeyboardButton(text="⬅️ Back", callback_data="back_to_settings")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


@router.message(Command("settings"))
async def show_settings(message: types.Message):
    """Show bot settings with interactive buttons"""
    chat_id = message.chat.id
    
    # Check if user is admin (optional - you can remove this check)
    # member = await message.bot.get_chat_member(chat_id, message.from_user.id)
    # if member.status not in ['administrator', 'creator']:
    #     await message.answer("❌ Only administrators can access settings.")
    #     return
    
    settings_text = f"""
⚙️ **Bot Settings** 🎵

📍 **Chat:** {message.chat.title}
🆔 **Chat ID:** `{chat_id}`

**Current Configuration:**
"""
    
    settings = get_chat_settings(chat_id)
    settings_text += f"""
🎶 **Play Mode:** {settings['play_mode'].replace('_', ' ').title()}
⏭️ **Skip Mode:** {settings['skip_mode'].replace('_', ' ').title()}
⏹️ **Stop Mode:** {settings['stop_mode'].replace('_', ' ').title()}
📊 **Queue Limit:** {'Unlimited' if settings['queue_limit'] == 0 else settings['queue_limit']}
🔄 **Auto Skip:** {'✅ ON' if settings['auto_skip'] else '❌ OFF'}
📢 **Log Actions:** {'✅ ON' if settings['log_actions'] else '❌ OFF'}

━━━━━━━━━━━━━━━━━━
💡 Tap buttons below to customize settings.
"""
    
    keyboard = build_settings_keyboard(chat_id)
    await message.answer(settings_text, reply_markup=keyboard, parse_mode='Markdown')


@router.callback_query(lambda c: c.data.startswith("set_"))
async def change_mode_setting(callback_query: types.CallbackQuery):
    """Handle mode setting changes"""
    chat_id = callback_query.message.chat.id
    setting_type = callback_query.data.replace("set_", "")
    
    keyboard = build_mode_selection_keyboard(setting_type)
    setting_name = setting_type.replace("_", " ").title()
    
    await callback_query.message.edit_text(
        f"⚙️ **Select {setting_name}**\n\nChoose who can use this command:",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )
    await callback_query.answer()


@router.callback_query(lambda c: c.data.startswith("mode_"))
async def select_mode(callback_query: types.CallbackQuery):
    """Handle mode selection"""
    chat_id = callback_query.message.chat.id
    parts = callback_query.data.split("_")
    setting_type = "_".join(parts[1:-1])  # e.g., play_mode, skip_mode
    mode_value = parts[-1]  # e.g., everyone, admin_only
    
    update_chat_setting(chat_id, setting_type, mode_value)
    
    await callback_query.answer(f"✅ {setting_type.replace('_', ' ').title()} set to {mode_value.replace('_', ' ').title()}")
    
    # Show updated settings
    keyboard = build_settings_keyboard(chat_id)
    settings_text = f"""
⚙️ **Settings Updated!** ✅

**{setting_type.replace('_', ' ').title()}:** {mode_value.replace('_', ' ').title()}

━━━━━━━━━━━━━━━━━━
💡 This change takes effect immediately.
"""
    await callback_query.message.edit_text(settings_text, reply_markup=keyboard, parse_mode='Markdown')


@router.callback_query(lambda c: c.data == "toggle_auto_skip")
async def toggle_auto_skip(callback_query: types.CallbackQuery):
    """Toggle auto skip setting"""
    chat_id = callback_query.message.chat.id
    settings = get_chat_settings(chat_id)
    
    new_value = not settings['auto_skip']
    update_chat_setting(chat_id, 'auto_skip', new_value)
    
    await callback_query.answer(f"{'✅ Auto Skip Enabled' if new_value else '❌ Auto Skip Disabled'}")
    
    # Show updated settings
    keyboard = build_settings_keyboard(chat_id)
    await callback_query.message.edit_reply_markup(reply_markup=keyboard)


@router.callback_query(lambda c: c.data == "toggle_log_actions")
async def toggle_log_actions(callback_query: types.CallbackQuery):
    """Toggle log actions setting"""
    chat_id = callback_query.message.chat.id
    settings = get_chat_settings(chat_id)
    
    new_value = not settings['log_actions']
    update_chat_setting(chat_id, 'log_actions', new_value)
    
    await callback_query.answer(f"{'📢 Logging Enabled' if new_value else '🔇 Logging Disabled'}")
    
    # Show updated settings
    keyboard = build_settings_keyboard(chat_id)
    await callback_query.message.edit_reply_markup(reply_markup=keyboard)


@router.callback_query(lambda c: c.data == "set_queue_limit")
async def set_queue_limit(callback_query: types.CallbackQuery):
    """Handle queue limit setting"""
    chat_id = callback_query.message.chat.id
    settings = get_chat_settings(chat_id)
    
    # Cycle through common limits: 0 (unlimited) -> 5 -> 10 -> 20 -> 0
    limits = [0, 5, 10, 20]
    current_idx = limits.index(settings['queue_limit']) if settings['queue_limit'] in limits else 0
    new_limit = limits[(current_idx + 1) % len(limits)]
    
    update_chat_setting(chat_id, 'queue_limit', new_limit)
    
    limit_text = 'Unlimited' if new_limit == 0 else f'{new_limit} songs'
    await callback_query.answer(f"📊 Queue Limit set to {limit_text}")
    
    # Show updated settings
    keyboard = build_settings_keyboard(chat_id)
    await callback_query.message.edit_reply_markup(reply_markup=keyboard)


@router.callback_query(lambda c: c.data == "reset_settings")
async def reset_settings_cmd(callback_query: types.CallbackQuery):
    """Reset all settings to default"""
    chat_id = callback_query.message.chat.id
    reset_chat_settings(chat_id)
    
    await callback_query.answer("🔄 Settings reset to default!")
    
    # Show updated settings
    keyboard = build_settings_keyboard(chat_id)
    settings_text = """
⚙️ **Settings Reset!** 🔄

All settings have been restored to their default values.

━━━━━━━━━━━━━━━━━━
💡 Default configuration restored.
"""
    await callback_query.message.edit_text(settings_text, reply_markup=keyboard, parse_mode='Markdown')


@router.callback_query(lambda c: c.data == "back_to_settings")
async def back_to_settings(callback_query: types.CallbackQuery):
    """Return to main settings menu"""
    chat_id = callback_query.message.chat.id
    keyboard = build_settings_keyboard(chat_id)
    
    settings = get_chat_settings(chat_id)
    settings_text = f"""
⚙️ **Bot Settings** 🎵

📍 **Chat:** {callback_query.message.chat.title}

**Current Configuration:**
🎶 Play: {settings['play_mode'].replace('_', ' ').title()}
⏭️ Skip: {settings['skip_mode'].replace('_', ' ').title()}
⏹️ Stop: {settings['stop_mode'].replace('_', ' ').title()}
📊 Queue: {'Unlimited' if settings['queue_limit'] == 0 else settings['queue_limit']}
🔄 Auto Skip: {'✅ ON' if settings['auto_skip'] else '❌ OFF'}
📢 Logs: {'✅ ON' if settings['log_actions'] else '❌ OFF'}
"""
    
    await callback_query.message.edit_text(settings_text, reply_markup=keyboard, parse_mode='Markdown')
    await callback_query.answer()
