#!/bin/bash

# Deploy GodVCMusicBot to VPS Server via SSH Key Authentication
# This script deploys the latest sound fix update

echo "🚀 Deploying GodVCMusicBot to Server..."
echo "========================================"
echo ""

# Configuration
SERVER_USER="root"
SERVER_HOST="45.143.228.160"
SSH_KEY_PATH="$HOME/.ssh/id_rsa"  # Change if using different key
BOT_DIR="~/GodVCMusicBot"

# Check if SSH key exists
if [ ! -f "$SSH_KEY_PATH" ]; then
    echo "❌ SSH key not found at $SSH_KEY_PATH"
    echo "Please create one with: ssh-keygen -t rsa -b 4096"
    exit 1
fi

# Test SSH connection
echo "🔑 Testing SSH connection..."
ssh -i "$SSH_KEY_PATH" -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" "echo '✅ SSH connection successful!'" 

if [ $? -ne 0 ]; then
    echo "❌ SSH connection failed!"
    echo "Make sure:"
    echo "1. Your SSH key is added to the server (~/.ssh/authorized_keys)"
    echo "2. SSH key permissions are correct (chmod 600 ~/.ssh/id_rsa)"
    echo "3. Server is accessible"
    exit 1
fi

echo ""
echo "📦 Deploying latest updates..."
echo ""

# Deploy commands via SSH
ssh -i "$SSH_KEY_PATH" "$SERVER_USER@$SERVER_HOST" << 'EOF'
set -e

echo "📥 Pulling latest changes from GitHub..."
cd ~/GodVCMusicBot || { echo "❌ Bot directory not found!"; exit 1; }
git pull origin main

if [ $? -eq 0 ]; then
    echo "✅ Git pull successful!"
    echo ""
    
    echo "📦 Checking dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt --upgrade --quiet
    
    echo ""
    echo "🔄 Restarting bot service..."
    systemctl restart godvcbot
    
    # Wait for service to start
    sleep 3
    
    echo ""
    echo "=============================================="
    echo "✅ Deployment Complete!"
    echo "=============================================="
    echo ""
    echo "🔊 Latest Changes Applied:"
    echo "   ✓ Fixed no sound in VC issue"
    echo "   ✓ Simplified ffmpeg parameters"
    echo "   ✓ Improved audio compatibility"
    echo "   ✓ Volume boost optimized (1.5x)"
    echo ""
    
    echo "📊 Service Status:"
    systemctl status godvcbot --no-pager | grep -E "(Active|Status)"
    echo ""
    
    echo "📋 Recent Logs (last 10 lines):"
    journalctl -u godvcbot -n 10 --no-pager
    echo ""
    
    echo "=============================================="
    echo "🎉 Bot is ready with sound fix!"
    echo "=============================================="
    echo ""
    echo "Useful Commands:"
    echo "  View logs:     journalctl -u godvcbot -f"
    echo "  Check status:  systemctl status godvcbot"
    echo "  Restart:       systemctl restart godvcbot"
    echo "  Stop:          systemctl stop godvcbot"
    echo ""
else
    echo "❌ Failed to pull updates. Please check your connection."
    exit 1
fi
EOF

# Check deployment success
if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "✅ Deployment Successful!"
    echo "========================================"
    echo ""
    echo "🧪 Test the sound fix now:"
    echo "   1. Join a voice chat"
    echo "   2. Send: /play never gonna give you up"
    echo "   3. Verify clear audio playback"
    echo ""
else
    echo ""
    echo "❌ Deployment failed. Please check SSH connection and try again."
    exit 1
fi
