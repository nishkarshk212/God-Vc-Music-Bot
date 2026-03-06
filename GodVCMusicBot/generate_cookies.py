"""
YouTube Cookie Exporter for GodVCMusicBot
This helps you export cookies from your browser to use with yt-dlp
"""

import os
import sys

def print_instructions():
    print("=" * 60)
    print("🍪 YouTube Cookie Setup for GodVCMusicBot")
    print("=" * 60)
    print()
    print("📋 Step-by-Step Instructions:")
    print()
    print("1️⃣  Install Browser Extension:")
    print("   Chrome/Edge: 'Get cookies.txt LOCALLY'")
    print("   Firefox: 'cookies.txt'")
    print("   Link: https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc")
    print()
    print("2️⃣  Export YouTube Cookies:")
    print("   a. Go to youtube.com in your browser")
    print("   b. Sign in to your Google account")
    print("   c. Click the extension icon")
    print("   d. Click 'Export' or 'Download'")
    print("   e. Save as 'youtube_cookies.txt'")
    print()
    print("3️⃣  Upload to Server:")
    print("   scp youtube_cookies.txt root@140.245.240.202:~/GodVCMusicBot/GodVCMusicBot/")
    print()
    print("4️⃣  Restart Bot:")
    print("   ssh root@140.245.240.202")
    print("   systemctl restart godvcbot")
    print()
    print("=" * 60)
    print()

if __name__ == "__main__":
    print_instructions()
