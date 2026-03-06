#!/bin/bash

# Deployment Script for GodVCMusicBot
# This script deploys the bot from GitHub to a VPS server

echo "🚀 Starting GodVCMusicBot Deployment..."
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/nishkarshk212/God-Vc-Music-Bot.git"
BOT_DIR="GodVCMusicBot"
PYTHON_VERSION="3.9"

echo -e "${YELLOW}📦 Step 1: Updating system packages...${NC}"
apt update && apt upgrade -y

echo -e "${YELLOW}🔧 Step 2: Installing required packages...${NC}"
apt install -y python3 python3-pip python3-venv git curl wget ffmpeg

echo -e "${YELLOW}🐍 Step 3: Checking Python version...${NC}"
python3 --version

echo -e "${YELLOW}📂 Step 4: Creating bot directory...${NC}"
cd ~
mkdir -p $BOT_DIR
cd $BOT_DIR

echo -e "${YELLOW}📥 Step 5: Cloning repository...${NC}"
git clone "$REPO_URL" .
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Repository cloned successfully!${NC}"
else
    echo -e "${RED}❌ Failed to clone repository${NC}"
    exit 1
fi

echo -e "${YELLOW}🌐 Step 6: Creating virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

echo -e "${YELLOW}📦 Step 7: Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dependencies installed!${NC}"
else
    echo -e "${RED}❌ Failed to install dependencies${NC}"
    exit 1
fi

echo -e "${YELLOW}⚙️ Step 8: Creating .env file...${NC}"
cat > .env << 'EOF'
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

# Channel Promo (Fill these in)
CHANNEL_PROMO_NAME=
CHANNEL_PROMO_CONTENT=
CHANNEL_PROMO_LINK=

# Group Promo (Fill these in)
GROUP_PROMO_NAME=
GROUP_PROMO_TOPIC=
GROUP_PROMO_LINK=

# Bot Promo (Fill these in)
BOT_PROMO_NAME=Ultra VC Music Bot
BOT_PROMO_FEATURES=Play songs in VC, queue system, animated player
BOT_PROMO_LINK=
EOF

echo -e "${GREEN}✅ .env file created!${NC}"
echo -e "${RED}⚠️  IMPORTANT: Edit .env file with your credentials!${NC}"

echo -e "${YELLOW}🔒 Step 9: Setting proper permissions...${NC}"
chmod 600 .env

echo -e "${YELLOW}📝 Step 10: Creating systemd service...${NC}"
cat > /etc/systemd/system/godvcbot.service << EOF
[Unit]
Description=GodVCMusicBot Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$HOME/$BOT_DIR
ExecStart=$HOME/$BOT_DIR/venv/bin/python3 $HOME/$BOT_DIR/GodVCMusicBot/bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=godvcbot

[Install]
WantedBy=multi-user.target
EOF

echo -e "${YELLOW}🔄 Step 11: Reloading systemd and enabling service...${NC}"
systemctl daemon-reload
systemctl enable godvcbot

echo ""
echo "========================================"
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo ""
echo "📋 Next Steps:"
echo "1. Edit the .env file: nano ~/GodVCMusicBot/.env"
echo "2. Add your API credentials and tokens"
echo "3. Start the bot: systemctl start godvcbot"
echo "4. Check status: systemctl status godvcbot"
echo "5. View logs: journalctl -u godvcbot -f"
echo ""
echo "🔧 Useful Commands:"
echo "  Start:    systemctl start godvcbot"
echo "  Stop:     systemctl stop godvcbot"
echo "  Restart:  systemctl restart godvcbot"
echo "  Status:   systemctl status godvcbot"
echo "  Logs:     journalctl -u godvcbot -f"
echo "  Disable:  systemctl disable godvcbot"
echo ""
echo -e "${GREEN}🎉 Your bot is ready to deploy!${NC}"
