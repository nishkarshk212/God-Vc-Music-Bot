#!/bin/bash

# Force Update Script - Forces server to match GitHub exactly
# WARNING: This will discard any uncommitted changes on the server

SERVER_IP="140.245.240.202"
USERNAME="root"
REPO_URL="https://github.com/nishkarshk212/God-Vc-Music-Bot.git"

echo "🚀 GodVCMusicBot - FORCE Update Deployment"
echo "==========================================="
echo ""
echo "⚠️  WARNING: This will DISCARD all local changes on server!"
echo ""
echo "📋 Server Details:"
echo "   IP: $SERVER_IP"
echo "   User: $USERNAME"
echo "   Repo: $REPO_URL"
echo ""
echo "⚠️  This will:"
echo "   1. Connect to your server"
echo "   2. Stop the bot"
echo "   3. FORCE reset to match GitHub (discarding local changes)"
echo "   4. Pull latest changes from GitHub"
echo "   5. Update dependencies"
echo "   6. Restart the bot"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

echo ""
echo "🔄 Starting force update..."
echo ""

# SSH and run force update commands
ssh -o StrictHostKeyChecking=no ${USERNAME}@${SERVER_IP} bash << 'ENDSSH'
#!/bin/bash

export REPO_URL="https://github.com/nishkarshk212/God-Vc-Music-Bot.git"

echo "📦 Step 1: Stopping bot service..."
systemctl stop godvcbot

echo "📥 Step 2: Navigating to bot directory..."
cd ~/GodVCMusicBot || { echo "❌ Cannot find GodVCMusicBot directory"; exit 1; }

echo "🔄 Step 3: Force resetting to match GitHub..."
git fetch origin
git reset --hard origin/main || { echo "❌ Git reset failed"; exit 1; }

echo "🧹 Step 4: Cleaning untracked files..."
git clean -fd

echo "🌐 Step 5: Activating virtual environment..."
source venv/bin/activate

echo "📦 Step 6: Updating Python packages..."
pip install --upgrade pip
cd GodVCMusicBot || { echo "❌ Cannot find GodVCMusicBot subdirectory"; exit 1; }
pip install -r requirements.txt || { echo "❌ Pip install failed"; exit 1; }
cd ..

echo ""
echo "✅ Update complete! Bot code updated."
echo ""
echo "⚠️  IMPORTANT: Your .env file should be preserved if it's in .gitignore"
echo ""
echo "🔄 Restarting bot service..."
systemctl daemon-reload
systemctl restart godvcbot

echo ""
echo "==========================================="
echo "✅ Force Update Complete!"
echo "==========================================="
echo ""
echo "Bot Status:"
systemctl status godvcbot --no-pager | head -n 15

echo ""
echo "Recent logs:"
journalctl -u godvcbot --no-pager -n 20

echo ""
echo "View live logs:"
echo "  journalctl -u godvcbot -f"
echo ""

ENDSSH

echo ""
echo "🎉 Force update finished!"
echo ""
echo "To view logs in real-time:"
echo "  ssh root@140.245.240.202 'journalctl -u godvcbot -f'"
echo
