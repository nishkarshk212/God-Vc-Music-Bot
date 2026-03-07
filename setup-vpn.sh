#!/bin/bash

# VPN Setup Script for GodVCMusicBot
# This installs and configures WireGuard VPN to bypass YouTube blocks

echo "🔧 Setting up VPN for YouTube access..."
echo "========================================"

# Install WireGuard
echo "📦 Installing WireGuard..."
apt update
apt install -y wireguard resolvconf

echo "✅ WireGuard installed!"
echo ""
echo "⚠️  IMPORTANT: You need to get a free WireGuard config from:"
echo "   https://www.vpnbook.com/free-openvpn-configs"
echo "   OR use a paid service like NordVPN/ExpressVPN"
echo ""
echo "Once you have a .ovpn or .conf file, upload it to:"
echo "   /root/wireguard.conf"
echo ""
echo "Then run: systemctl start wg-quick@wg0"
echo ""

# Create systemd service to auto-start VPN
cat > /etc/systemd/system/youtube-vpn.service << 'EOF'
[Unit]
Description=WireGuard VPN for YouTube Access
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/wg-quick up wg0
ExecStop=/usr/bin/wg-quick down wg0

[Install]
WantedBy=multi-user.target
EOF

echo "✅ VPN service created!"
echo ""
echo "Next steps:"
echo "1. Get a WireGuard/OpenVPN config file"
echo "2. Upload it: scp your-config.conf root@140.245.240.202:/root/wireguard.conf"
echo "3. Enable it: systemctl enable youtube-vpn"
echo "4. Start it: systemctl start youtube-vpn"
echo "5. Test: curl ifconfig.me (should show VPN IP)"
