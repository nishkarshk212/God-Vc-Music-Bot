#!/bin/bash
echo "🔌 Connecting to ProtonVPN..."
echo ""
ssh root@140.245.240.202 << 'ENDSSH'
echo "📊 Starting WireGuard..."
wg-quick up wg0 2>&1 | grep -v "debconf"

echo ""
echo "⏳ Waiting for connection..."
sleep 3

echo ""
echo "🌐 Your new IP:"
NEW_IP=$(curl -s --max-time 10 ifconfig.me)
echo "$NEW_IP"

if [ "$NEW_IP" != "140.245.240.202" ]; then
    echo ""
    echo "✅ SUCCESS! VPN connected!"
    echo "   Old IP: 140.245.240.202"
    echo "   New IP: $NEW_IP"
    echo ""
    echo "🎵 Testing YouTube..."
    cd ~/GodVCMusicBot/GodVCMusicBot/core
    cp ytdl_vpn.py ytdl.py 2>/dev/null || true
    systemctl restart godvcbot
    echo "✅ Bot restarted with VPN!"
else
    echo ""
    echo "❌ VPN not working - still showing server IP"
fi
ENDSSH
