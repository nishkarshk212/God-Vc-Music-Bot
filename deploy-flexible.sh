#!/bin/bash

# Flexible Deploy Script - Ask for Server IP
echo "🚀 GodVCMusicBot Deployment"
echo "============================"
echo ""

# Ask for server IP
read -p "Enter your server IP (or press Enter for 45.143.228.160): " SERVER_IP
SERVER_IP=${SERVER_IP:-45.143.228.160}

echo ""
echo "📡 Testing connection to $SERVER_IP ..."
echo ""

# Test connection
if ping-c 2 -W 2 "$SERVER_IP" &>/dev/null; then
   echo "✅ Server is reachable!"
else
   echo "⚠️  Server not responding to ping"
   read -p "Continue anyway? (y/n): " continue_deploy
   if [ "$continue_deploy" != "y" ]; then
       echo "❌ Deployment cancelled"
       exit 1
    fi
fi

echo ""
echo "🔑 Testing SSH connection..."

# Try SSH connection
ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no root@"$SERVER_IP" "echo '✅ SSH connected!'" 2>/dev/null

if [ $? -ne 0 ]; then
   echo "❌ SSH connection failed!"
   echo ""
   echo "Manual deployment instructions:"
   echo "================================"
   echo "1. Connect manually: ssh root@$SERVER_IP"
   echo "2. Run these commands:"
   echo ""
   echo "   cd ~/GodVCMusicBot"
   echo "   git pull origin main"
   echo "   source venv/bin/activate"
   echo "   pip install -r requirements.txt --upgrade"
   echo "   systemctl restart godvcbot"
   echo "   systemctl status godvcbot"
   echo ""
   exit 1
fi

echo ""
echo "✅ SSH works! Starting automated deployment..."
echo ""

# Deploy via SSH
ssh root@"$SERVER_IP" << 'ENDSSH'
set -e
cd ~/GodVCMusicBot
git pull origin main
source venv/bin/activate
pip install -r requirements.txt --upgrade --quiet
systemctl restart godvcbot
sleep 3
echo ""
echo "=================================="
echo "✅ Deployment Complete!"
echo "=================================="
systemctl status godvcbot --no-pager | grep -E "(Active|Status)"
echo ""
journalctl -u godvcbot -n 10 --no-pager
ENDSSH

if [ $? -eq 0 ]; then
   echo ""
   echo "🎉 SUCCESS! Bot deployed with sound fix!"
   echo "Test in Telegram: /play never gonna give you up"
else
   echo ""
   echo "❌ Deployment had issues. Check logs above."
fi
