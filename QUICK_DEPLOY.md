# 🚀 Quick Deploy - GodVCMusicBot

## ⚡ One-Command Deployment (Recommended)

From your **Mac terminal**, run this single command:

```bash
./auto-deploy.sh
```

This will automatically:
1. Connect to your server
2. Install all dependencies
3. Clone the repository
4. Set up everything needed
5. Create systemd service
6. Prepare the bot for running

---

## 📋 Server Details (Pre-configured)

- **IP Address:** 140.245.240.202
- **Username:** root
- **Password:** Akshay343402355468
- **Port:** 22
- **Repository:** https://github.com/nishkarshk212/God-Vc-Music-Bot.git

---

## 🔧 Alternative Methods

### Method 1: Manual SSH + Script

```bash
# Step 1: Connect to server
ssh root@140.245.240.202

# Step 2: Download and run deployment script
wget https://raw.githubusercontent.com/nishkarshk212/God-Vc-Music-Bot/main/deploy.sh
chmod +x deploy.sh
./deploy.sh
```

### Method 2: Copy Script Then Run

```bash
# From Mac terminal
scp deploy.sh root@140.245.240.202:/root/
ssh root@140.245.240.202 "chmod +x deploy.sh && ./deploy.sh"
```

### Method 3: Fully Manual

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed manual steps.

---

## ⚙️ Post-Deployment Configuration

After deployment completes, you MUST configure the `.env` file:

```bash
# SSH into server
ssh root@140.245.240.202

# Edit .env file
nano ~/GodVCMusicBot/.env
```

### Required Values:

```ini
API_ID=33830507                    # Your API ID from my.telegram.org
API_HASH=your_api_hash_here        # Your API Hash
BOT_TOKEN=your_bot_token_here      # Token from @BotFather
SESSION_STRING=your_session_here   # Pyrogram session string
LOG_CHANNEL_ID=@log_x_bott        # Your log channel
OWNER_ID=your_telegram_id         # Your Telegram user ID
```

Save with `Ctrl+X`, then `Y`, then `Enter`.

---

## ▶️ Starting the Bot

```bash
# Start the bot
systemctl start godvcbot

# Check status
systemctl status godvcbot

# View logs
journalctl -u godvcbot -f
```

---

## 🎯 Verify Deployment

Test your bot:

1. Open Telegram
2. Find your bot
3. Send `/start`
4. Send `/play <song_name>`
5. Check if it joins voice chat and plays music
6. Check @log_x_bott channel for notifications

---

## 📊 Monitoring Commands

```bash
# Real-time logs
journalctl -u godvcbot -f

# Last 50 lines
journalctl -u godvcbot -n 50

# Today's logs
journalctl -u godvcbot --since today

# Resource usage
top -p $(pgrep -f bot.py)

# Check if running
ps aux | grep bot.py
```

---

## 🔄 Updating Bot

```bash
cd ~/GodVCMusicBot
git pull origin main
systemctl restart godvcbot
```

---

## 🛑 Stopping Bot

```bash
# Stop temporarily
systemctl stop godvcbot

# Start again
systemctl start godvcbot

# Restart
systemctl restart godvcbot

# Disable auto-start on boot
systemctl disable godvcbot
```

---

## 🆘 Troubleshooting

### Bot won't start?
```bash
# Check error logs
journalctl -u godvcbot -n 100

# Check .env configuration
cat ~/GodVCMusicBot/.env

# Test manually
cd ~/GodVCMusicBot
source venv/bin/activate
python3 GodVCMusicBot/bot.py
```

### Can't connect to server?
```bash
# From Mac terminal
ping 140.245.240.202

# Check SSH
ssh -v root@140.245.240.202
```

### Memory issues?
```bash
# Restart bot
systemctl restart godvcbot

# Clear cache
cd ~/GodVCMusicBot
rm -rf __pycache__
```

---

## 📞 Support Contact

For issues or questions:
- **Telegram:** @Jayden_212
- **GitHub:** https://github.com/nishkarshk212/God-Vc-Music-Bot/issues

---

## ✅ Checklist

Before starting:
- [ ] Server is accessible via SSH
- [ ] You have root/sudo access
- [ ] Internet connection is stable
- [ ] Sufficient disk space (>1GB free)
- [ ] Python 3.8+ available

After deployment:
- [ ] Bot responds to /start
- [ ] Bot can play music
- [ ] Logs appear in @log_x_bott
- [ ] Systemd service is running
- [ ] Auto-restart works
- [ ] Settings panel accessible

---

**Made with ❤️ by @nishkarshk212**
