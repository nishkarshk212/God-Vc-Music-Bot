#!/bin/bash

# Automated Deployment Script - Run from Mac
# This script connects to server and deploys the bot automatically

SERVER_IP="140.245.240.202"
USERNAME="root"
PASSWORD="Akshay343402355468"
REPO_URL="https://github.com/nishkarshk212/God-Vc-Music-Bot.git"

echo "🚀 GodVCMusicBot Automated Deployment"
echo "======================================"
echo ""
echo "📋 Server Details:"
echo "   IP: $SERVER_IP"
echo "   User: $USERNAME"
echo "   Repo: $REPO_URL"
echo ""
echo "⚠️  This will:"
echo "   1. Connect to your server"
echo "   2. Install all dependencies"
echo "   3. Clone the repository"
echo "   4. Set up virtual environment"
echo "   5. Install Python packages"
echo "   6. Create systemd service"
echo "   7. Start the bot"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

echo ""
echo "🔌 Connecting to server..."
echo ""

# SSH and run deployment commands
ssh ${USERNAME}@${SERVER_IP} bash << 'ENDSSH'
#!/bin/bash

export REPO_URL="https://github.com/nishkarshk212/God-Vc-Music-Bot.git"

echo "📦 Step 1: Updating system..."
apt update && apt upgrade -y

echo "🔧 Step 2: Installing dependencies..."
apt install -y python3 python3-pip python3-venv git curl wget ffmpeg

echo "📂 Step 3: Creating directory..."
cd ~
mkdir -p GodVCMusicBot
cd GodVCMusicBot

echo "📥 Step 4: Cloning repository..."
git clone "$REPO_URL" . || { echo "❌ Git clone failed"; exit 1; }

echo "🌐 Step 5: Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "📦 Step 6: Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt || { echo "❌ Pip install failed"; exit 1; }

echo "⚙️ Step 7: Creating .env file..."
cat > .env << EOF
# Required Configuration
API_ID=your_api_id_here
API_HASH=your_api_hash_here
BOT_TOKEN=your_bot_token_here
SESSION_STRING=your_session_string_here

# Log Channel
LOG_CHANNEL_ID=@log_x_bott

# Owner Configuration
OWNER_ID=

# Promo Configuration
AUTHORIZED_USER=Jayden_212
PROMO_TIME=300

# Channel Promo
CHANNEL_PROMO_NAME=
CHANNEL_PROMO_CONTENT=
CHANNEL_PROMO_LINK=

# Group Promo
GROUP_PROMO_NAME=
GROUP_PROMO_TOPIC=
GROUP_PROMO_LINK=

# Bot Promo
BOT_PROMO_NAME=Ultra VC Music Bot
BOT_PROMO_FEATURES=Play songs in VC, queue system, animated player
BOT_PROMO_LINK=
EOF

chmod 600 .env

echo "📝 Step 8: Creating systemd service..."
cat > /etc/systemd/system/godvcbot.service << EOF
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
EOF

echo "🔄 Step 9: Enabling service..."
systemctl daemon-reload
systemctl enable godvcbot

echo ""
echo "======================================"
echo "✅ Deployment Complete!"
echo "======================================"
echo ""
echo "⚠️  IMPORTANT: Configure your .env file!"
echo "   Run: nano ~/GodVCMusicBot/.env"
echo ""
echo "Add your:"
echo "  - API_ID"
echo "  - API_HASH"
echo "  - BOT_TOKEN"
echo "  - SESSION_STRING"
echo ""
echo "Then start the bot:"
echo "  systemctl start godvcbot"
echo ""
echo "Check status:"
echo "  systemctl status godvcbot"
echo ""
echo "View logs:"
echo "  journalctl -u godvcbot -f"
echo ""

ENDSSH

echo ""
echo "🎉 Deployment finished!"
echo ""
echo "Next steps:"
echo "1. SSH into server: ssh root@140.245.240.202"
echo "2. Edit .env file: nano ~/GodVCMusicBot/.env"
echo "3. Add your credentials"
echo "4. Start bot: systemctl start godvcbot"
echo "5. Check logs: journalctl -u godvcbot -f"
