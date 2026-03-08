#!/bin/bash
# Cleanup duplicate bot copy

echo "🗑️ Removing duplicate GodVCMusicBot..."
rm -rf /root/GodVCMusicBot

echo "✅ Duplicate removed!"
echo ""
echo "📊 Remaining bot locations:"
ls -d /root/* | grep -E 'music_bot|GodVCMusicBot' 2>/dev/null || echo "Only music_bot remains"

echo ""
echo "✅ Cleanup complete!"
