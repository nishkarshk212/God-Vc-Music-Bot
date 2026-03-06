# God-VC-Music-Bot 🎵

A powerful Telegram VC Music Bot built with Python, aiogram, and PyTgCalls.

## ✨ Features

### 🎶 Core Features
- **Play Music** from YouTube in Voice Chat
- **Video Support** with /vplay command
- **Queue System** - Add multiple songs to queue
- **Player Controls** - Pause, Resume, Skip, Stop
- **Seek Functionality** - Forward/Rewind by 5 seconds
- **Animated Progress** - Real-time slider updates

### 📊 Advanced Features
- **Settings Panel** - Customize bot behavior per group
  - Play Mode (Everyone/Admin Only/Requester Only)
  - Skip Mode (Everyone/Admin Only/Requester Only)
  - Stop Mode (Everyone/Admin Only/Requester Only)
  - Queue Limit settings
  - Auto Skip toggle
  - Log Actions toggle

### 🔔 Notifications & Logging
- **Log Channel Integration** - All actions sent to @log_x_bott
  - Song play notifications with user info
  - Queue add notifications with position
  - Skip notifications with track details
  - Stop notifications with last track info
  - Voice chat participant count
  - Group details (ID, name, link)
  - User details (ID, username, name)

### 🛠️ Auto-Maintenance System
- **Auto-Restart** every 6 hours for optimal performance
- **Auto Cache Cleaning** - Removes temporary files
- **Auto Bug Fixing** - Self-healing mechanism
- **Crash Recovery** - Automatic restart on failure
- **Memory Optimization** - Garbage collection
- **All logged to channel** - Complete transparency

### 📢 Promotional System
- **Channel Promo** (/promo) - Promote Telegram channels
- **Group Promo** (/promogroup) - Promote groups
- **Bot Promo** (/promobot) - Promote bots
- **Authorization Control** - Only @Jayden_212 can use promo commands

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Telegram API credentials
- MongoDB connection string

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/nishkarshk212/God-Vc-Music-Bot.git
cd God-Vc-Music-Bot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
   - Copy `.env.example` to `.env`
   - Fill in your credentials:
     - `API_ID`
     - `API_HASH`
     - `BOT_TOKEN`
     - `SESSION_STRING`
     - `LOG_CHANNEL_ID`
     - Other optional settings

4. **Run the bot**
```bash
python bot.py
```

## 📁 Project Structure

```
GodVCMusicBot/
├── core/           # Core functionality (call, queue, ytdl)
├── plugins/        # Command handlers (play, skip, stop, etc.)
├── utils/          # Utilities (logger, settings, maintenance)
├── bot.py          # Main bot file
├── config.py       # Configuration loader
└── requirements.txt # Dependencies
```

## ⚙️ Configuration

### Required Variables
- `API_ID` - Telegram API ID
- `API_HASH` - Telegram API Hash
- `BOT_TOKEN` - Bot Token from BotFather
- `SESSION_STRING` - Pyrogram session string
- `LOG_CHANNEL_ID` - Channel for logs (@log_x_bott)

### Optional Variables
- `OWNER_ID` - Bot owner's user ID
- `AUTHORIZED_USER` - Username for promo commands
- `PROMO_TIME` - Interval for promotional messages
- Various promo configuration options

## 🎮 Commands

### Music Commands
- `/play <song>` - Play audio song
- `/vplay <video>` - Play video
- `/pause` - Pause current song
- `/resume` - Resume paused song
- `/skip` - Skip to next song
- `/stop` - Stop music and disconnect
- `/queue` - Show song queue

### Settings & Admin
- `/settings` - Open bot settings panel
- `/promo` - Send channel promotion
- `/promobot` - Send bot promotion
- `/promogroup` - Send group promotion

## 🔧 Auto-Maintenance

The bot features an enterprise-level auto-maintenance system:

### Features
- **6-Hour Auto-Restart** - Prevents memory leaks
- **Cache Cleaning** - Removes temporary files
- **Bug Auto-Fix** - Self-healing mechanisms
- **Crash Recovery** - Instant restart on failure
- **Real-time Logging** - All actions sent to log channel

### What Gets Logged
- Bot startup/shutdown
- Auto-restart events
- Maintenance reports
- Crash alerts with stack traces
- Recovery actions
- Uptime statistics

## 📝 Notes

- Session files are automatically excluded from git
- Environment variables should never be committed
- Log channel receives comprehensive action logs
- Settings are per-chat and persist across restarts

## 🤝 Support

For issues or questions, contact: @Jayden_212

## 📄 License

This project is provided as-is for educational purposes.

---

**Made with ❤️ by @nishkarshk212**
