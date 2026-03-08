# 🚀 FINAL DEPLOYMENT SCRIPT - GODVCMUSICBOT

## Quick Deploy Command (Copy & Paste):

```bash
sshpass -p "Akshay343402355468" ssh -o StrictHostKeyChecking=no -p 22 root@140.245.240.202 "
cd /root/GodVCMusicBot && \
echo '🧹 Cleaning cache...' && \
find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null && \
find . -type f -name '*.pyc' -delete 2>/dev/null && \
echo '🔧 Installing dependencies...' && \
source venv/bin/activate && \
pip uninstall py-tgcalls ntgcalls -y 2>&1 | grep -v 'Successfully uninstalled' && \
pip install --no-cache-dir 'py-tgcalls==1.2.9' 'ntgcalls==2.1.0' 2>&1 | tail -3 && \
echo '✅ Dependencies installed' && \
echo '🔄 Restarting service...' && \
systemctl daemon-reload && \
systemctl restart godvc && \
sleep 5 && \
echo '' && \
echo '📊 STATUS:' && \
ps aux | grep 'GodVCMusicBot.*bot.py' | grep -v grep && \
echo '' && \
systemctl status godvc --no-pager | head -12 && \
echo '' && \
echo '✅ DEPLOYMENT COMPLETE!'
"
```

## Manual Deployment Steps:

### 1. Upload Files to Server
```bash
# Method 1: Tar-pipe (recommended)
cd /Users/nishkarshkr/Desktop/TITANIC\ BOTS/GodVCMusicBot
tar --exclude='*.session*' --exclude='__pycache__' --exclude='*.pyc' --exclude='logs' --exclude='downloads' -czf - . | \
sshpass -p "Akshay343402355468" ssh -o StrictHostKeyChecking=no -p 22 root@140.245.240.202 \
"cat > /tmp/godvc.tar.gz && cd /root/GodVCMusicBot && tar -xzf /tmp/godvc.tar.gz && rm /tmp/godvc.tar.gz"

# Method 2: Individual file upload
sshpass -p "Akshay343402355468" scp -P 22 -o StrictHostKeyChecking=no GodVCMusicBot/plugins/clearqueue.py root@140.245.240.202:/root/GodVCMusicBot/plugins/
```

### 2. SSH into Server
```bash
sshpass -p "Akshay343402355468" ssh -o StrictHostKeyChecking=no -p 22 root@140.245.240.202
```

### 3. Install Dependencies
```bash
cd /root/GodVCMusicBot
source venv/bin/activate
pip uninstall py-tgcalls ntgcalls -y
pip install --no-cache-dir 'py-tgcalls==1.2.9' 'ntgcalls==2.1.0'
exit
```

### 4. Register clearqueue Plugin
Edit bot.py on server:
```bash
sshpass -p "Akshay343402355468" ssh -o StrictHostKeyChecking=no -p 22 root@140.245.240.202 "
cd /root/GodVCMusicBot && \
sed -i.bak 's/from plugins import start, play, vplay, ping, stop, skip, player_controls, queue_cmd, promo, settings, debug$/from plugins import start, play, vplay, ping, stop, skip, player_controls, queue_cmd, promo, settings, debug, clearqueue/' bot.py && \
grep -q 'dp.include_router(clearqueue.router)' bot.py || sed -i '/dp.include_router(debug.router)/a dp.include_router(clearqueue.router)' bot.py && \
rm bot.py.bak
"
```

### 5. Restart Bot
```bash
sshpass -p "Akshay343402355468" ssh -o StrictHostKeyChecking=no -p 22 root@140.245.240.202 "
systemctl daemon-reload && \
systemctl restart godvc && \
sleep 3 && \
ps aux | grep 'GodVCMusicBot.*bot.py' | grep -v grep && \
echo '' && \
systemctl status godvc --no-pager | head -10
"
```

---

## Verify Deployment:

### Check if Running:
```bash
sshpass -p "Akshay343402355468" ssh -o StrictHostKeyChecking=no -p 22 root@140.245.240.202 "systemctl is-active godvc"
```

### Test /clearqueue Command:
1. Join voice chat in a test group
2. Add songs: `/play song1`, `/play song2`, `/play song3`
3. Clear queue: `/clearqueue`
4. Bot should respond: "✅ Queue cleared! Removed X songs"

### Check Logs:
```bash
sshpass -p "Akshay343402355468" ssh -o StrictHostKeyChecking=no -p 22 root@140.245.240.202 "journalctl -u godvc --no-pager -n 20 | tail -10"
```

---

## Features Deployed:

✅ **NEW**: `/clearqueue` command
- Admin-only permission
- Clears entire queue
- Logs to @logx_212
- Shows count of removed songs

✅ **Skip Animation Removed**
- Instant skip (no 3.5s delay)
- Better UX

✅ **Auto-Stop Feature**
- Monitors VC participants
- Stops after 30s empty
- Auto-clears queue

✅ **Enhanced Audio**
- 320kbps STUDIO quality
- 48kHz sample rate
- 13 FFmpeg params

✅ **Auto-Restart**
- Never-stop configuration
- 5-second restart delay
- Watchdog monitoring

---

## Troubleshooting:

### If Bot Won't Start:
```bash
sshpass -p "Akshay343402355468" ssh -o StrictHostKeyChecking=no -p 22 root@140.245.240.202 "
cd /root/GodVCMusicBot && \
source venv/bin/activate && \
python bot.py 2>&1 | head -50
"
```

### Check Error Logs:
```bash
sshpass -p "Akshay343402355468" ssh -o StrictHostKeyChecking=no -p 22 root@140.245.240.202 "journalctl -u godvc -f"
```

### Force Restart:
```bash
sshpass -p "Akshay343402355468" ssh -o StrictHostKeyChecking=no -p 22 root@140.245.240.202 "pkill -9 -f 'GodVCMusicBot.*bot.py' && sleep 2 && systemctl start godvc"
```

---

**Deployment Date**: Sun 2026-03-08  
**Version**: v2.3 Enhanced Edition  
**New Feature**: /clearqueue command  
**Status**: Ready to Deploy
