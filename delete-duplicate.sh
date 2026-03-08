#!/bin/bash
echo "🗑️ Deleting duplicate /root/GodVCMusicBot..."
rm -rf /root/GodVCMusicBot
echo "✅ Duplicate deleted!"
echo ""
echo "📊 Remaining bot locations:"
ls -d /root/* 2>/dev/null | grep -E 'music_bot|GodVCMusicBot' || echo "Only music_bot remains ✅"
echo ""
echo "✅ Cleanup complete!"
