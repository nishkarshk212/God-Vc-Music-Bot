#!/bin/bash

# Simple Cookies Upload Script
SERVER_IP="140.245.240.202"
USERNAME="root"

echo "🍪 Uploading YouTube Cookies to Server..."
echo ""

# Upload cookies
echo "📤 Uploading cookies file..."
scp "/Users/nishkarshkr/Desktop/TITANIC BOTS/youtube_cookies.txt" root@${SERVER_IP}:~/GodVCMusicBot/GodVCMusicBot/youtube_cookies.txt

if [ $? -eq 0 ]; then
    echo "✅ Cookies uploaded successfully!"
    echo ""
    echo "🔧 Setting permissions on server..."
    
    ssh root@${SERVER_IP} << 'EOF'
cd ~/GodVCMusicBot/GodVCMusicBot
chmod 600 youtube_cookies.txt
ls -lh youtube_cookies.txt
echo ""
echo "✅ Permissions set!"
EOF
    
    echo ""
    echo "🎉 Done! Now test your bot with /play command"
else
    echo "❌ Upload failed. Try manual method:"
    echo ""
    echo "1. SSH into server:"
    echo "   ssh root@140.245.240.202"
    echo ""
    echo "2. Create cookies file manually:"
    echo "   cd ~/GodVCMusicBot/GodVCMusicBot"
    echo "   nano youtube_cookies.txt"
    echo ""
    echo "3. Paste your cookies content and save (Ctrl+X, Y, Enter)"
fi
