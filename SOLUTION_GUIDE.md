# Complete Solution Guide for YouTube IP Block

## Problem
Your server's IP (140.245.240.202) is completely blocked by YouTube at the network level.

## Solutions Implemented

### Solution 1: VPN Integration ✅
**File**: `setup-vpn.sh`

**Steps to activate:**

1. **Get a free WireGuard config:**
   - Visit: https://www.vpnbook.com/free-openvpn-configs
   - OR use: https://vpnmentor.com/tool/vpn-setup-wizard/
   - Download a US or EU based config

2. **Upload config to server:**
   ```bash
   # Rename your downloaded file to wireguard.conf
   scp /path/to/wireguard.conf root@140.245.240.202:/root/wireguard.conf
   ```

3. **Install and enable VPN:**
   ```bash
   ssh root@140.245.240.202
   cd ~/GodVCMusicBot
   chmod +x setup-vpn.sh
   ./setup-vpn.sh
   
   # Enable VPN on boot
   systemctl enable youtube-vpn
   
   # Start VPN
   systemctl start youtube-vpn
   
   # Verify VPN is working
   curl ifconfig.me
   # Should show VPN IP, not your server IP
   ```

4. **Test YouTube access:**
   ```bash
   python3 GodVCMusicBot/core/ytdl_vpn.py
   # Should detect VPN and work!
   ```

---

### Solution 2: Spotify Fallback 🎵
**File**: `spotify-integration.py`

**Steps to setup:**

1. **Get Spotify API credentials:**
   - Go to: https://developer.spotify.com/dashboard
   - Create an app
   - Copy Client ID and Client Secret

2. **Update spotify-integration.py:**
   ```python
   SPOTIFY_CLIENT_ID = "your_actual_client_id"
   SPOTIFY_CLIENT_SECRET = "your_actual_secret"
   ```

3. **Install spotipy on server:**
   ```bash
   ssh root@140.245.240.202
   cd ~/GodVCMusicBot
   source venv/bin/activate
   pip install spotipy
   ```

4. **Test Spotify search:**
   ```bash
   python3 spotify-integration.py
   ```

---

### Solution 3: Combined Approach (Recommended) 🚀

The bot will now:
1. Check if VPN is active
2. If yes, use VPN for all YouTube requests
3. If no VPN, try rotating proxies
4. If that fails, fall back to Spotify search

**To use the VPN-enhanced version:**

```bash
ssh root@140.245.240.202

# Stop bot
systemctl stop godvcbot

# Backup old ytdl
cd ~/GodVCMusicBot/GodVCMusicBot/core
cp ytdl.py ytdl_backup.py

# Use VPN version
cp ../ytdl_vpn.py ytdl.py

# Restart bot
systemctl restart godvcbot

# Watch logs
journalctl -u godvcbot -f
```

---

## Testing

Once VPN is setup:

1. **Check VPN status:**
   ```bash
   ssh root@140.245.240.202 'curl ifconfig.me'
   # Should show different IP than your server
   ```

2. **Test music playback:**
   ```
   /play never gonna give you up
   ```

3. **Watch logs:**
   ```bash
   ssh root@140.245.240.202 'journalctl -u godvcbot -f'
   ```

You should see:
```
✅ VPN detected! IP: 185.220.101.XX
🔍 Searching for: never gonna give you up
  ✅ Success via Invidious!
```

---

## Quick Commands Reference

### VPN Management
```bash
# Start VPN
systemctl start youtube-vpn

# Stop VPN
systemctl stop youtube-vpn

# Check status
systemctl status youtube-vpn

# View VPN IP
curl ifconfig.me
```

### Bot Management
```bash
# Restart bot
systemctl restart godvcbot

# View logs
journalctl -u godvcbot -f

# Check status
systemctl status godvcbot
```

---

## Alternative: Free VPN Options

If you don't want to configure manually:

1. **ProtonVPN** (Free tier, unlimited data):
   ```bash
   wget https://repo.protonvpn.com/debian/dists/stable/main/binary-all/protonvpn-stable-release_1.0.3_all.deb
   dpkg -i protonvpn-stable-release_1.0.3_all.deb
   apt update && apt install protonvpn
   protonvpn connect
   ```

2. **Windscribe** (Free 10GB/month):
   ```bash
   wget -O windscribe-repo.deb https://repo.windscribe.com/debian/windscribe-repo.deb
   dpkg -i windscribe-repo.deb
   apt update && apt install windscribe-cli
   windscribe login
   windscribe connect
   ```

---

## Next Steps

1. Choose a VPN provider (ProtonVPN recommended for free unlimited)
2. Install and connect VPN on server
3. Test YouTube access
4. Bot will automatically use VPN when available

Need help? Check the logs and share them!
