# 🚀 Quick Deployment Commands

## ✅ Git Repository is Already Updated!

Your GitHub repository already has the complete sound fix at commit `ba9e7d5`.

---

## 📋 Manual Deployment Steps

Copy and paste these commands into your terminal:

### Step 1: Connect to Server
```bash
ssh root@45.143.228.160
```

### Step 2: Update and Deploy (run on server)
```bash
cd ~/GodVCMusicBot
git pull origin main
source venv/bin/activate
pip install -r requirements.txt --upgrade
systemctl restart godvcbot
systemctl status godvcbot
```

### Step 3: Check Logs (optional)
```bash
journalctl -u godvcbot -f
```

---

## 🧪 Test the Sound Fix

After deployment, test in Telegram:

```
/play never gonna give you up
```

**Expected:** Clear audio with good volume! ✅

---

## 📊 What's Deployed

✅ **Commit:** `ba9e7d5` (includes sound fix `55fe078`)  
✅ **Fix:** Simplified ffmpeg parameters  
✅ **Volume:** 1.5x boost  
✅ **Quality:** 48kHz sample rate, stereo  

---

## ✨ One-Command Alternative

If SSH keys are set up, you can run:

```bash
cd "/Users/nishkarshkr/Desktop/TITANIC BOTS"
./deploy-to-server.sh
```

But if that fails, use the manual steps above!
