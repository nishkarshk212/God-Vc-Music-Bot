#!/bin/bash

# Alternative Deployment Script - Copy & Paste for Manual SSH
# This generates commands you can copy and paste into your SSH session

echo "📋 Manual Deployment Commands"
echo "================================"
echo ""
echo "Since SSH connection timed out, please follow these steps:"
echo ""
echo "1️⃣  Connect to your server manually:"
echo "   ssh root@45.143.228.160"
echo ""
echo "2️⃣  Once connected, run these commands:"
echo ""
echo "----------------------------------------"
cat << 'COMMANDS'
# Navigate to bot directory
cd ~/GodVCMusicBot

# Pull latest updates from GitHub
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart the bot
systemctl restart godvcbot

# Check status (wait a few seconds)
sleep 3
systemctl status godvcbot --no-pager

# View recent logs
journalctl -u godvcbot -n 20 --no-pager
COMMANDS
echo "----------------------------------------"
echo ""
echo "3️⃣  Test the sound fix in Telegram:"
echo "   Send: /play never gonna give you up"
echo ""
echo "✅ Expected: Clear audio with good volume!"
echo ""
echo "📊 What's being deployed:"
echo "   - Sound fix (simplified ffmpeg params)"
echo "   - Volume boost 1.5x"
echo "   - 48kHz sample rate"
echo "   - Stereo audio"
echo ""
