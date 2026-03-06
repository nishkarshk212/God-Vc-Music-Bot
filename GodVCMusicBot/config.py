import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
SESSION_STRING = os.getenv("SESSION_STRING", "")
_owner_id = os.getenv("OWNER_ID", "0")
try:
    OWNER_ID = int(_owner_id)
except (TypeError, ValueError):
    OWNER_ID = 0
LOG_CHANNEL_ID = os.getenv("LOG_CHANNEL_ID", "")

# Promo configuration
AUTHORIZED_USER = os.getenv("AUTHORIZED_USER", "Jayden_212")
PROMO_TIME = int(os.getenv("PROMO_TIME", "300"))  # Default 5 minutes in seconds
BOT_PROMO_NAME = os.getenv("BOT_PROMO_NAME", "Ultra VC Music Bot")
BOT_PROMO_FEATURES = os.getenv("BOT_PROMO_FEATURES", "Play songs in VC, queue system, animated player")
BOT_PROMO_LINK = os.getenv("BOT_PROMO_LINK", "")
CHANNEL_PROMO_NAME = os.getenv("CHANNEL_PROMO_NAME", "")
CHANNEL_PROMO_CONTENT = os.getenv("CHANNEL_PROMO_CONTENT", "")
CHANNEL_PROMO_LINK = os.getenv("CHANNEL_PROMO_LINK", "")
GROUP_PROMO_NAME = os.getenv("GROUP_PROMO_NAME", "")
GROUP_PROMO_TOPIC = os.getenv("GROUP_PROMO_TOPIC", "")
GROUP_PROMO_LINK = os.getenv("GROUP_PROMO_LINK", "")
