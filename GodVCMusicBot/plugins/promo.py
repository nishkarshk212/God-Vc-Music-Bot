from aiogram import Router, types
from aiogram.filters import Command
from utils.promo_format import CHANNEL_PROMO, GROUP_PROMO, BOT_PROMO
from config import (
    AUTHORIZED_USER, 
    BOT_PROMO_NAME, 
    BOT_PROMO_FEATURES, 
    BOT_PROMO_LINK,
    CHANNEL_PROMO_NAME,
    CHANNEL_PROMO_CONTENT,
    CHANNEL_PROMO_LINK,
    GROUP_PROMO_NAME,
    GROUP_PROMO_TOPIC,
    GROUP_PROMO_LINK
)

router = Router()


def is_authorized(username: str) -> bool:
    """Check if user is authorized to send promos"""
    return username == AUTHORIZED_USER or f"@{username}" == AUTHORIZED_USER


@router.message(Command("promo"))
async def channel_promo_handler(message: types.Message):
    """Send channel promotional message - Only for authorized user"""
    # Check authorization
    username = message.from_user.username or ""
    if not is_authorized(username):
        await message.answer("❌ You are not authorized to use this command.")
        return
    
    # Check if channel promo is configured
    if not CHANNEL_PROMO_NAME or not CHANNEL_PROMO_LINK:
        await message.answer("⚠️ Channel promo not configured. Please set CHANNEL_PROMO_NAME and CHANNEL_PROMO_LINK in .env")
        return
    
    text = CHANNEL_PROMO.format(
        name=CHANNEL_PROMO_NAME,
        content=CHANNEL_PROMO_CONTENT or "Amazing content",
        link=CHANNEL_PROMO_LINK
    )
    
    await message.answer(
        text,
        disable_web_page_preview=True
    )


@router.message(Command("promobot"))
async def bot_promo_handler(message: types.Message):
    """Send bot promotional message - Only for authorized user"""
    # Check authorization
    username = message.from_user.username or ""
    if not is_authorized(username):
        await message.answer("❌ You are not authorized to use this command.")
        return
    
    # Check if bot promo is configured
    if not BOT_PROMO_NAME or not BOT_PROMO_LINK:
        await message.answer("⚠️ Bot promo not configured. Please set BOT_PROMO_NAME and BOT_PROMO_LINK in .env")
        return
    
    text = BOT_PROMO.format(
        name=BOT_PROMO_NAME,
        features=BOT_PROMO_FEATURES or "Amazing features",
        link=BOT_PROMO_LINK
    )
    
    await message.answer(
        text,
        disable_web_page_preview=True
    )


@router.message(Command("promogroup"))
async def group_promo_handler(message: types.Message):
    """Send group promotional message - Only for authorized user"""
    # Check authorization
    username = message.from_user.username or ""
    if not is_authorized(username):
        await message.answer("❌ You are not authorized to use this command.")
        return
    
    # Check if group promo is configured
    if not GROUP_PROMO_NAME or not GROUP_PROMO_LINK:
        await message.answer("⚠️ Group promo not configured. Please set GROUP_PROMO_NAME and GROUP_PROMO_LINK in .env")
        return
    
    text = GROUP_PROMO.format(
        name=GROUP_PROMO_NAME,
        topic=GROUP_PROMO_TOPIC or "General discussion",
        link=GROUP_PROMO_LINK
    )
    
    await message.answer(
        text,
        disable_web_page_preview=True
    )
