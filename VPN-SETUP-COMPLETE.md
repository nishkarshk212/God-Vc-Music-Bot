# ✅ VPN Setup Complete - Manual Commands Guide

## Your WireGuard Config is Installed!

The config file has been uploaded to: `/etc/wireguard/wg0.conf`

---

## 🚀 Quick Start Commands

### 1. **Start VPN** (SSH into server first)
```bash
ssh root@140.245.240.202
# Password: Akshay343402355468

# Start WireGuard
wg-quick up wg0
```

### 2. **Check if VPN is Connected**
```bash
# Check interface
ip addr show wg0

# Should show:
#   inet 10.2.0.2/32 scope global wg0

# Check WireGuard status
wg show

# Should show peer information and handshake
```

### 3. **Test New IP Address**
```bash
curl ifconfig.me

# BEFORE VPN: Shows 140.245.240.202 (your server)
# AFTER VPN: Shows different IP (e.g., 149.88.x.x - Canada/Europe)
```

### 4. **Enable Auto-Start on Boot**
```bash
systemctl enable wg-quick@wg0
systemctl start wg-quick@wg0
```

### 5. **Test YouTube Access**
```bash
cd ~/GodVCMusicBot/GodVCMusicBot/core

# Use VPN-enhanced version
cp ytdl_vpn.py ytdl.py

# Test search
python3 -c "from ytdl import search_youtube; result = search_youtube('test'); print('Success!' if result else 'Failed')"

# Restart bot
cd ~/GodVCMusicBot
systemctl restart godvcbot

# Watch logs
journalctl -u godvcbot -f
```

---

## 📊 Status Check Commands

### Check VPN Status
```bash
# Is WireGuard running?
systemctl status wg-quick@wg0

# Show active connections
wg show

# Current IP
curl ifconfig.me
```

### Check Bot Status
```bash
# Is bot running?
systemctl status godvcbot

# Recent logs
journalctl -u godvcbot -n 20

# Live logs
journalctl -u godvcbot -f
```

---

## 🔧 Troubleshooting

### If VPN Won't Start
```bash
# Check config file exists
ls -lh /etc/wireguard/wg0.conf

# Check for errors
wg-quick up wg0 2>&1 | head -20

# Try restarting
wg-quick down wg0
wg-quick up wg0
```

### If YouTube Still Blocked
```bash
# Verify VPN IP is different
echo "Server IP: 140.245.240.202"
echo "VPN IP: $(curl ifconfig.me)"

# If same IP, VPN not working!
# Reconnect:
pkill wg-quick
wg-quick up wg0
```

### Check Which Server You're Connected To
Your config shows: `Endpoint = 149.88.97.110:51820`
This is a ProtonVPN server (likely Canada or Netherlands based on IP)

---

## 🎯 Expected Results

After VPN connects successfully:

1. **IP Address Changes**
   ```bash
   curl ifconfig.me
   # Should show: 149.88.x.x or similar (NOT 140.245.240.202)
   ```

2. **YouTube Works**
   ```bash
   cd ~/GodVCMusicBot/GodVCMusicBot/core
   python3 -c "from ytdl import search_youtube; r = search_youtube('never gonna give you up'); print(f'Found: {r[\"title\"]}')"
   # Should print song title without errors
   ```

3. **Bot Plays Music**
   In Telegram: `/play never gonna give you up`
   
   Logs should show:
   ```
   ✅ VPN detected! IP: 149.88.XX.XX
   🔍 Searching for: never gonna give you up
     → Testing Invidious: https://yewtu.be
     ✅ Success via Invidious!
   🎵 Started playback
   ```

---

## ⚡ One-Liner Status Check

Run this to see everything at once:

```bash
ssh root@140.245.240.202 'echo "=== VPN Status ===" && (ip addr show wg0 | grep inet || echo "❌ VPN not active") && echo "" && echo "=== Your IP ===" && curl -s ifconfig.me && echo "" && echo "=== Bot Status ===" && systemctl is-active godvcbot'
```

Expected output:
```
=== VPN Status ===
    inet 10.2.0.2/32 scope global wg0
=== Your IP ===
149.88.97.XX  ← Different from server IP!
=== Bot Status ===
active
```

---

## 🎉 Success Indicators

✅ VPN connected when you see:
- `inet 10.2.0.2/32` in `ip addr show wg0`
- Different IP in `curl ifconfig.me`
- `wg show` displays peer handshake

✅ YouTube working when:
- No "All strategies failed" errors
- Logs show "✅ Success via Invidious!"
- Music plays in voice chat

---

## 📞 Need Help?

Share these outputs:
```bash
# 1. VPN status
ip addr show wg0

# 2. Your current IP
curl ifconfig.me

# 3. WireGuard peers
wg show

# 4. Last 20 bot log lines
journalctl -u godvcbot -n 20 --no-pager
```
