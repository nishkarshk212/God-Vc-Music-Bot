# GodVCMusicBot Deployment Guide

## 📋 Prerequisites

- VPS/Server with Ubuntu/Debian (provided: 140.245.240.202)
- Root access or sudo privileges
- Python 3.8+ installed
- Git installed
- FFmpeg installed

## 🚀 Quick Deployment Steps

### Option 1: Automated Deployment (Recommended)

#### From your Mac, run the deployment script via SSH:

```bash
# Connect to server and run deployment
ssh root@140.245.240.202 "bash -s" < deploy.sh
```

OR

```bash
# Step 1: Copy deployment script to server
scp deploy.sh root@140.245.240.202:/root/

# Step 2: SSH into server
ssh root@140.245.240.202

# Step 3: Run deployment script
chmod +x deploy.sh
./deploy.sh
```

---

### Option 2: Manual Deployment

#### Step 1: Connect to Server
```bash
ssh root@140.245.240.202
# Password: Akshay343402355468
```

#### Step 2: Update System
```bash
apt update && apt upgrade -y
```

#### Step 3: Install Dependencies
```bash
apt install -y python3 python3-pip python3-venv git curl wget ffmpeg
```

#### Step 4: Clone Repository
```bash
cd ~
mkdir GodVCMusicBot
cd GodVCMusicBot
git clone https://github.com/nishkarshk212/God-Vc-Music-Bot.git .
```

#### Step 5: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Step 6: Install Python Packages
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 7: Configure Environment
```bash
nano .env
```

Fill in your credentials:
- `API_ID` - Get from my.telegram.org
- `API_HASH` - Get from my.telegram.org
- `BOT_TOKEN` - Get from @BotFather
- `SESSION_STRING` - Generate using generate_session.py

#### Step 8: Create Systemd Service
```bash
nano /etc/systemd/system/godvcbot.service
```

Paste this content:
```ini
[Unit]
Description=GodVCMusicBot Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/GodVCMusicBot
ExecStart=/root/GodVCMusicBot/venv/bin/python3 /root/GodVCMusicBot/GodVCMusicBot/bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=godvcbot

[Install]
WantedBy=multi-user.target
```

Save and exit (Ctrl+X, Y, Enter)

#### Step 9: Enable and Start Service
```bash
systemctl daemon-reload
systemctl enable godvcbot
systemctl start godvcbot
```

#### Step 10: Check Status
```bash
systemctl status godvcbot
```

---

## 🔧 Managing Your Bot

### View Logs
```bash
# Real-time logs
journalctl -u godvcbot -f

# Last 100 lines
journalctl -u godvcbot -n 100

# Today's logs
journalctl -u godvcbot --since today
```

### Control Commands
```bash
# Start bot
systemctl start godvcbot

# Stop bot
systemctl stop godvcbot

# Restart bot
systemctl restart godvcbot

# Reload configuration
systemctl reload godvcbot

# Check status
systemctl status godvcbot

# Disable auto-start
systemctl disable godvcbot
```

### Update Bot
```bash
cd ~/GodVCMusicBot
git pull origin main
systemctl restart godvcbot
```

---

## 📱 Monitoring

### Check if bot is running
```bash
ps aux | grep bot.py
```

### Check resource usage
```bash
top -p $(pgrep -f bot.py)
```

### Check memory usage
```bash
free -h
```

### Check disk space
```bash
df -h
```

---

## 🔐 Security Recommendations

1. **Protect .env file**
   ```bash
   chmod 600 ~/GodVCMusicBot/.env
   ```

2. **Use SSH keys instead of password**
   ```bash
   # On your Mac
   ssh-keygen -t ed25519
   ssh-copy-id root@140.245.240.202
   ```

3. **Configure firewall (if using UFW)**
   ```bash
   ufw allow 22/tcp
   ufw enable
   ```

4. **Regular updates**
   ```bash
   apt update && apt upgrade -y
   ```

---

## ⚠️ Troubleshooting

### Bot won't start
```bash
# Check logs
journalctl -u godvcbot -n 50

# Check if port 22 is open
netstat -tulpn | grep :22
```

### Memory issues
```bash
# Restart bot
systemctl restart godvcbot

# Clear cache
cd ~/GodVCMusicBot
rm -rf __pycache__
```

### Python errors
```bash
# Reinstall dependencies
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

### Network issues
```bash
# Test internet connection
ping google.com

# Check DNS
cat /etc/resolv.conf
```

---

## 🎯 Post-Deployment Checklist

- [ ] Bot starts without errors
- [ ] Bot responds to /start command
- [ ] Bot can play music (/play command)
- [ ] Logs are sent to @log_x_bott channel
- [ ] Auto-maintenance system is active
- [ ] Settings panel works (/settings)
- [ ] Promo commands work (/promo, /promobot, /promogroup)
- [ ] Systemd service is enabled and running
- [ ] Bot auto-restarts on crash
- [ ] All permissions are correctly set

---

## 📞 Support

If you encounter issues:
1. Check logs: `journalctl -u godvcbot -f`
2. Verify .env configuration
3. Ensure all dependencies are installed
4. Check server resources (RAM, CPU, Disk)

---

## 🌟 Features Active After Deployment

✅ Music playback in voice chat
✅ Video support (/vplay)
✅ Queue system
✅ Player controls (pause, resume, skip, stop, seek)
✅ Settings panel with customizable modes
✅ Log channel notifications (@log_x_bott)
✅ Auto-restart every 6 hours
✅ Crash recovery system
✅ Cache auto-cleaning
✅ Promotional commands
✅ Voice chat participant tracking
✅ User and group details logging

---

**Made with ❤️ by @nishkarshk212**
