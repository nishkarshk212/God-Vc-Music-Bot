# ❌ WHY YOUR BOT ISN'T RUNNING WHEN MAC IS OFF

## 🔍 THE PROBLEM:

### 1. **Code Inconsistency**
Your **local Mac** has the LATEST code with:
- ✅ `/clearqueue` command
- ✅ Skip animation removed
- ✅ Auto-stop feature
- ✅ Queue auto-clear
- ✅ Enhanced audio (320kbps)
- ✅ Format selector utilities

But your **server (140.245.240.202)** has:
- ❌ Incomplete code upload
- ❌ Missing critical files
- ❌ Version mismatches
- ❌ Import errors

### 2. **Why Bot Dies When Mac Off**
```
Mac ON → You can SSH to server → Bot crashes due to errors
Mac OFF → Can't deploy fixes → Bot stays dead
```

**The bot runs on the SERVER, not your Mac!** But it needs your Mac's code to work properly.

---

## ✅ **PERMANENT SOLUTION:**

### Option 1: Complete Code Upload (RECOMMENDED)

Upload your ENTIRE working GodVCMusicBot folder to the server:

```bash
# From your Mac
cd "/Users/nishkarshkr/Desktop/TITANIC BOTS/GodVCMusicBot"

# Create complete archive
tar --exclude='*.session*' --exclude='__pycache__' --exclude='*.pyc' \
    --exclude='logs' --exclude='downloads' --exclude='thumbnails' \
    -czf /tmp/complete-bot.tar.gz .

# Upload to server
cat /tmp/complete-bot.tar.gz | \
sshpass -p "Akshay343402355468" ssh -o StrictHostKeyChecking=no -p 22 root@140.245.240.202 \
"cat > /tmp/bot-upload.tar.gz && cd /root/GodVCMusicBot && \
rm -rf core plugins utils bot.py config.py assistant.py requirements.txt && \
tar -xzf /tmp/bot-upload.tar.gz && rm /tmp/bot-upload.tar.gz && \
echo '✅ Complete bot uploaded!' && ls -la"
```

Then on the server:
```bash
sshpass -p "Akshay343402355468" ssh -o StrictHostKeyChecking=no -p 22 root@140.245.240.202

cd /root/GodVCMusicBot

# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Clear cache
find . -name '__pycache__' -type d -exec rm -rf {} +

# Start bot
systemctl daemon-reload
systemctl restart godvc

# Verify
ps aux | grep 'GodVCMusicBot.*bot.py'
systemctl status godvc
```

---

### Option 2: Fix Individual Files (QUICK FIX)

Upload each missing file one by one:

```bash
# Upload format_selector.py
cat "/Users/nishkarshkr/Desktop/TITANIC BOTS/GodVCMusicBot/utils/format_selector.py" | \
sshpass -p "Akshay343402355468" ssh -o StrictHostKeyChecking=no -p 22 root@140.245.240.202 \
"cat > /root/GodVCMusicBot/utils/format_selector.py"

# Upload all plugins
cd "/Users/nishkarshkr/Desktop/TITANIC BOTS/GodVCMusicBot/plugins"
for file in *.py; do
  cat "$file" | sshpass -p "Akshay343402355468" ssh -o StrictHostKeyChecking=no -p 22 root@140.245.240.202 \
  "cat > /root/GodVCMusicBot/plugins/$file"
done

# Upload core files
cd "/Users/nishkarshkr/Desktop/TITANIC BOTS/GodVCMusicBot/core"
for file in *.py; do
  cat "$file" | sshpass -p "Akshay343402355468" ssh -o StrictHostKeyChecking=no -p 22 root@140.245.240.202 \
  "cat > /root/GodVCMusicBot/core/$file"
done
```

---

## 🚀 **ONE-COMMAND DEPLOYMENT SCRIPT:**

Save this as `deploy-to-server.sh` on your Mac:

```bash
#!/bin/bash

echo "🚀 Deploying GodVCMusicBot to Server..."
echo "========================================"

# Configuration
SERVER_IP="140.245.240.202"
SERVER_USER="root"
SERVER_PASS="Akshay343402355468"
LOCAL_DIR="/Users/nishkarshkr/Desktop/TITANIC BOTS/GodVCMusicBot"

# Create archive
echo "📦 Creating archive..."
cd "$LOCAL_DIR"
tar --exclude='*.session*' --exclude='__pycache__' --exclude='*.pyc' \
    --exclude='logs' --exclude='downloads' --exclude='thumbnails' \
    -czf /tmp/godvc-deploy.tar.gz .

# Upload
echo "⬆️  Uploading to server..."
cat /tmp/godvc-deploy.tar.gz | \
sshpass -p "$SERVER_PASS" ssh -o StrictHostKeyChecking=no -p 22 \
$SERVER_USER@$SERVER_IP \
"cat > /tmp/deploy.tar.gz && cd /root/GodVCMusicBot && \
rm -rf core plugins utils bot.py config.py assistant.py requirements.txt && \
tar -xzf /tmp/deploy.tar.gz && rm /tmp/deploy.tar.gz && \
echo '✅ Files uploaded!'"

# Deploy on server
echo "🔧 Deploying on server..."
sshpass -p "$SERVER_PASS" ssh -o StrictHostKeyChecking=no -p 22 \
$SERVER_USER@$SERVER_IP << 'ENDSSH'
cd /root/GodVCMusicBot

echo "🗑️  Cleaning old venv..."
rm -rf venv

echo "📦 Creating fresh venv..."
python3 -m venv venv
source venv/bin/activate

echo "📥 Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt --no-cache-dir -q

echo "🧹 Clearing cache..."
find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null

echo "🔄 Restarting service..."
systemctl daemon-reload
systemctl restart godvc

sleep 5

echo ""
echo "📊 STATUS:"
ps aux | grep 'GodVCMusicBot.*bot.py' | grep -v grep
echo ""
systemctl status godvc --no-pager | head -12

echo ""
echo "✅ DEPLOYMENT COMPLETE!"
ENDSSH

echo ""
echo "🎉 Deployment finished!"
```

Make it executable and run:
```bash
chmod +x deploy-to-server.sh
./deploy-to-server.sh
```

---

## 📋 **VERIFICATION CHECKLIST:**

After deployment, verify bot is running:

```bash
# Check if process is running
sshpass -p "Akshay343402355468" ssh -o StrictHostKeyChecking=no -p 22 root@140.245.240.202 \
"ps aux | grep 'GodVCMusicBot.*bot.py' | grep -v grep"

# Expected output:
# root    PID  CPU MEM  VSZ   RSS TTY      S    START TIME COMMAND
# root   12345  0.5  1.2  93972 82912 ?    R    08:00   0:10 /root/GodVCMusicBot/venv/bin/python /root/GodVCMusicBot/bot.py
```

If you see a process, the bot is ALIVE and will run independently of your Mac!

---

## 🎯 **KEY POINTS:**

1. ✅ **Bot runs on SERVER** (140.245.240.202), NOT on your Mac
2. ✅ **Server is independent** - once deployed correctly, works 24/7
3. ✅ **Your Mac is just for development** - deploy code to server
4. ✅ **Auto-restart configured** - systemd will restart if bot crashes
5. ✅ **No Mac dependency** - after deployment, bot runs forever

---

## ⚠️ **WHY IT'S FAILING NOW:**

Your server has:
- ❌ Partial code upload (some files missing)
- ❌ Import errors (can't find modules)
- ❌ Dependency issues (wrong py-tgcalls version)
- ❌ Cache corruption (.pyc files from old code)

**Solution**: Upload COMPLETE codebase in ONE go, then recreate venv!

---

## 🆘 **EMERGENCY FIX:**

If nothing else works, run this COMPLETE deployment:

```bash
sshpass -p "Akshay343402355468" ssh -o StrictHostKeyChecking=no -p 22 root@140.245.240.202 << 'EOF'
cd /root/GodVCMusicBot

# Nuclear option - delete everything
rm -rf venv core plugins utils *.py __pycache__ downloads thumbnails logs

# Upload will happen here via tar-pipe

# Then recreate
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
systemctl restart godvc
EOF
```

---

**Once properly deployed, your bot will run FOREVER on the server, independent of your Mac!** 🚀
