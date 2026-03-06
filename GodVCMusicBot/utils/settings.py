"""
Bot Settings Storage (In-Memory)
In production, use a database for persistence
"""

# Global settings storage per chat
chat_settings = {}


def get_chat_settings(chat_id: int) -> dict:
    """Get settings for a specific chat"""
    if chat_id not in chat_settings:
        # Default settings
        chat_settings[chat_id] = {
            "play_mode": "everyone",  # everyone, admin_only, requester_only
            "skip_mode": "everyone",  # everyone, admin_only, requester_only
            "stop_mode": "everyone",  # everyone, admin_only, requester_only
            "queue_limit": 0,  # 0 = unlimited
            "auto_skip": False,  # Auto skip after stop
            "log_actions": True,  # Log all actions to channel
        }
    return chat_settings[chat_id]


def update_chat_setting(chat_id: int, key: str, value):
    """Update a specific setting for a chat"""
    settings = get_chat_settings(chat_id)
    settings[key] = value
    chat_settings[chat_id] = settings


def reset_chat_settings(chat_id: int):
    """Reset settings to default for a chat"""
    if chat_id in chat_settings:
        del chat_settings[chat_id]
