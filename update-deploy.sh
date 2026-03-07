#!/bin/bash

# Quick Update Script - Updates existing deployment from GitHub
# Run this from your Mac to update the server with latest changes

SERVER_IP="140.245.240.202"
USERNAME="root"
REPO_URL="https://github.com/nishkarshk212/God-Vc-Music-Bot.git"

echo "🚀 GodVCMusicBot - Quick Update Deployment"
echo "==========================================="
echo ""
echo "📋 Server Details:"
echo "   IP: $SERVER_IP"
echo "   User: $USERNAME"
echo "   Repo: $REPO_URL"
echo ""
echo "⚠️  This will:"
echo "   1. Connect to your server"
echo "   2. Stop the bot"
echo "   3. Pull latest changes from GitHub"
echo "   4. Update dependencies"
echo "   5. Restart the bot"
echo ""
echo "🔄 Starting update..."
echo ""

# SSH and run update commands
ssh ${USERNAME}@${SERVER_IP} bash << 'ENDSSH'
#!/bin/bash

export REPO_URL="https://github.com/nishkarshk212/God-Vc-Music-Bot.git"

echo "📦 Step 1: Stopping bot service..."
systemctl stop godvcbot

echo "📥 Step 2: Navigating to bot directory..."
cd ~/GodVCMusicBot || { echo "❌ Cannot find GodVCMusicBot directory"; exit 1; }

echo "🔄 Step 3: Pulling latest changes from GitHub..."
git pull origin main || { echo "❌ Git pull failed"; exit 1; }

echo "🌐 Step 4: Activating virtual environment..."
source venv/bin/activate

echo "📦 Step 5: Updating Python packages..."
pip install --upgrade pip
cd GodVCMusicBot || { echo "❌ Cannot find GodVCMusicBot subdirectory"; exit 1; }
pip install -r requirements.txt || { echo "❌ Pip install failed"; exit 1; }
cd ..

echo ""
echo "✅ Update complete! Bot code updated."
echo ""
echo "⚠️  IMPORTANT: Your .env file is preserved (not overwritten)"
echo ""
echo "🔄 Restarting bot service..."
systemctl daemon-reload
systemctl restart godvcbot

echo ""
echo "==========================================="
echo "✅ Update Complete!"
echo "==========================================="
echo ""
echo "Bot Status:"
systemctl status godvcbot --no-pager | head -n 10

echo ""
echo "View live logs:"
echo "  journalctl -u godvcbot -f"
echo ""

ENDSSH

echo ""
echo "🎉 Update finished!"
echo ""
echo "To view logs in real-time:"
echo "  ssh root@140.245.240.202 'journalctl -u godvcbot -f'"
echo
