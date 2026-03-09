#!/bin/bash

# Quick Update Script for GodVCMusicBot
# Run this on your VPS server to update with latest fixes

echo "🚀 Updating GodVCMusicBot with Latest Fixes..."
echo "=============================================="
echo ""

cd ~/GodVCMusicBot || { echo "❌ Bot directory not found!"; exit 1; }

echo "📥 Pulling latest changes from GitHub..."
git pull origin main

if [ $? -eq 0 ]; then
    echo "✅ Git pull successful!"
    echo ""
    
    echo "📦 Installing any updated dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt --upgrade
    
    echo ""
    echo "🔄 Restarting bot service..."
    systemctl restart godvcbot
    
    echo ""
    echo "=============================================="
    echo "✅ Update Complete!"
    echo ""
    echo "🔊 Latest Changes Applied:"
    echo "   ✓ Enhanced audio processing"
    echo "   ✓ Fixed VC sound issues"
    echo "   ✓ Improved unmute reliability"
    echo "   ✓ Better audio post-processing"
    echo ""
    echo "📊 Check status: systemctl status godvcbot"
    echo "📋 View logs: journalctl -u godvcbot -f"
    echo ""
else
    echo "❌ Failed to pull updates. Please check your connection."
    exit 1
fi
