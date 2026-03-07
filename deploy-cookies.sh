#!/bin/bash

# Deploy Cookies and Update Script
# Uploads YouTube cookies to server and updates bot code

SERVER_IP="140.245.240.202"
USERNAME="root"
COOKIES_FILE="/Users/nishkarshkr/Desktop/TITANIC BOTS/youtube_cookies.txt"

echo "🍪 GodVCMusicBot - Cookies Upload & Update"
echo "==========================================="
echo ""
echo "📋 Uploading:"
echo "   From: $COOKIES_FILE"
echo "   To: ~/GodVCMusicBot/GodVCMusicBot/youtube_cookies.txt"
echo ""
echo "🔄 This will also update code from GitHub"
echo ""

# First, update the code from GitHub
echo "🔄 Step 1: Updating code from GitHub..."
ssh ${USERNAME}@${SERVER_IP} << 'ENDSSH'
cd ~/GodVCMusicBot
systemctl stop godvcbot
git fetch origin
git reset --hard origin/main
git clean -fd
echo "✅ Code updated!"
ENDSSH

echo ""
echo "🍪 Step 2: Uploading cookies file..."

# Upload cookies using scp
scp ${COOKIES_FILE} ${USERNAME}@${SERVER_IP}:~/GodVCMusicBot/GodVCMusicBot/youtube_cookies.txt

if [ $? -eq 0 ]; then
    echo "✅ Cookies uploaded successfully!"
else
    echo "❌ Failed to upload cookies"
    exit 1
fi

echo ""
echo "⚙️ Step 3: Setting permissions and restarting..."

ssh ${USERNAME}@${SERVER_IP} << 'ENDSSH'
cd ~/GodVCMusicBot

# Set proper permissions for cookies
chmod 600 GodVCMusicBot/youtube_cookies.txt
chown root:root GodVCMusicBot/youtube_cookies.txt

# Verify cookies file exists
if [ -f GodVCMusicBot/youtube_cookies.txt ]; then
    echo "✅ Cookies file verified at: GodVCMusicBot/youtube_cookies.txt"
    ls -lh GodVCMusicBot/youtube_cookies.txt
else
    echo "❌ Cookies file not found!"
    exit 1
fi

# Activate virtual environment and verify yt-dlp
source venv/bin/activate
cd GodVCMusicBot
pip install -r requirements.txt
cd ..

# Restart bot
systemctl daemon-reload
systemctl restart godvcbot

echo ""
echo "✅ Bot restarted!"
echo ""
echo "📊 Service Status:"
systemctl status godvcbot --no-pager | head -n 10

echo ""
echo "📝 Recent Logs:"
journalctl -u godvcbot --no-pager -n 15

ENDSSH

echo ""
echo "==========================================="
echo "✅ Deployment Complete!"
echo "==========================================="
echo ""
echo "🎯 What's configured:"
echo "   ✓ Latest code from GitHub (with Invidious fallback)"
echo "   ✓ YouTube cookies uploaded and configured"
echo "   ✓ Bot service restarted"
echo ""
echo "🔍 The bot will now try in this order:"
echo "   1. Invidious instances (bypasses blocks)"
echo "   2. Cookie-based authentication"
echo "   3. Direct connection (last resort)"
echo ""
echo "📋 View live logs:"
echo "   ssh root@140.245.240.202 'journalctl -u godvcbot -f'"
echo ""
