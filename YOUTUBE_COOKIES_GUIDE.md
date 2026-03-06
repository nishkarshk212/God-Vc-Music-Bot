# 🍪 YouTube Cookie Setup Guide

## Why You Need Cookies

YouTube blocks automated requests from bots. By exporting cookies from your browser, the bot can use your authenticated session to access YouTube without restrictions.

---

## 📋 Step-by-Step Instructions

### **Step 1: Install Browser Extension**

Choose one of these extensions:

#### For Chrome/Edge/Brave:
- **Extension:** "Get cookies.txt LOCALLY"
- **Link:** https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc
- **Install:** Click "Add to Chrome"

#### For Firefox:
- **Extension:** "cookies.txt"
- **Link:** https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/
- **Install:** Click "Add to Firefox"

---

### **Step 2: Export YouTube Cookies**

1. **Open YouTube**
   - Go to https://youtube.com in your browser

2. **Sign In**
   - Make sure you're signed into your Google/YouTube account
   - If not signed in, click "Sign In" and log in

3. **Use the Extension**
   - Click the extension icon in your browser toolbar
   - You should see a list of cookies

4. **Export Cookies**
   - Click "Export" or "Download" button
   - Choose "Netscape HTTP Cookie File" format if asked
   - Save the file as `youtube_cookies.txt`

5. **Verify the File**
   - Open the downloaded file in a text editor
   - It should contain many lines starting with `.youtube.com` or `.google.com`
   - File size should be 5-20 KB

---

### **Step 3: Upload Cookies to Server**

From your Mac terminal:

```bash
# Navigate to where you downloaded the cookies
cd ~/Downloads

# Upload to server
scp youtube_cookies.txt root@140.245.240.202:~/GodVCMusicBot/GodVCMusicBot/
```

Enter password when prompted: `Akshay343402355468`

---

### **Step 4: Verify on Server**

```bash
# SSH into server
ssh root@140.245.240.202

# Check if file exists
ls -lh ~/GodVCMusicBot/GodVCMusicBot/youtube_cookies.txt

# Should show file size around 5-20K
```

---

### **Step 5: Restart Bot**

```bash
# Restart the bot
systemctl restart godvcbot

# Check status
systemctl status godvcbot

# View logs (watch for cookie confirmation)
journalctl -u godvcbot -f
```

You should see: `✅ Using cookies from: ...`

---

### **Step 6: Test the Bot**

1. Open Telegram
2. Find your bot
3. Send: `/play <any_song_name>`
4. The bot should now play music without authentication errors!

---

## 🔍 Troubleshooting

### **Cookies Expire After Some Time**

YouTube cookies expire after a few weeks/months. When they expire:

1. Re-export fresh cookies from your browser (Step 2)
2. Upload again (Step 3)
3. Restart bot: `systemctl restart godvcbot`

### **"No such file" Error**

Make sure the file is in the correct location:

```bash
# Check location
ssh root@140.245.240.202 "ls -la ~/GodVCMusicBot/GodVCMusicBot/youtube_cookies.txt"
```

If missing, re-upload:
```bash
scp youtube_cookies.txt root@140.245.240.202:~/GodVCMusicBot/GodVCMusicBot/
```

### **Still Getting Authentication Errors**

Try these alternatives:

#### Option A: Use Incognito/Private Window
1. Open incognito/private browser window
2. Sign into YouTube
3. Export cookies

#### Option B: Clear Old Cookies First
1. Clear YouTube cookies from your browser
2. Refresh YouTube page
3. Sign in again
4. Export fresh cookies

#### Option C: Try Different Browser
- If Chrome doesn't work, try Firefox or Edge

---

## 🔐 Security Notes

⚠️ **Important Security Practices:**

1. **Keep cookies private** - Don't share your cookie file publicly
2. **File permissions** - Server file should be readable only by root:
   ```bash
   chmod 600 ~/GodVCMusicBot/GodVCMusicBot/youtube_cookies.txt
   ```
3. **Regular updates** - Re-export cookies every few weeks
4. **Use secondary account** - Consider using a secondary Google account for the bot

---

## ✅ Success Indicators

You'll know it's working when:

- ✅ No "Sign in to confirm you're not a bot" errors in logs
- ✅ Bot responds quickly to `/play` commands
- ✅ Songs play without interruptions
- ✅ Logs show: `✅ Using cookies from: ...`

---

## 🆘 Quick Reference Commands

```bash
# Upload cookies
scp youtube_cookies.txt root@140.245.240.202:~/GodVCMusicBot/GodVCMusicBot/

# SSH to server
ssh root@140.245.240.202

# Check file exists
ls -lh ~/GodVCMusicBot/GodVCMusicBot/youtube_cookies.txt

# Set secure permissions
chmod 600 ~/GodVCMusicBot/GodVCMusicBot/youtube_cookies.txt

# Restart bot
systemctl restart godvcbot

# View logs
journalctl -u godvcbot -f

# Check bot status
systemctl status godvcbot
```

---

## 🎉 That's It!

Once cookies are set up, your bot will work smoothly without YouTube authentication issues. Just remember to refresh cookies every few weeks!

**Made with ❤️ by @nishkarshk212**
