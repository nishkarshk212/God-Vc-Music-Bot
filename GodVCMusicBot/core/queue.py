from collections import defaultdict

class ChatQueueManager:
    """Queue manager with auto-clear on VC end detection"""
    
    def __init__(self):
        self.music_queue = defaultdict(list)
        self.vc_ended_chats = set()  # Track chats where VC has ended
    
    def add_to_queue(self, chat_id, item):
        # Check if VC ended - reject new items if so
        if chat_id in self.vc_ended_chats:
            print(f"⚠️ Rejecting queue addition - VC ended for chat {chat_id}")
            return False
        self.music_queue[chat_id].append(item)
        print(f"✅ Added to queue: {item.get('title', 'Unknown')} in chat {chat_id}")
        return True
    
    def get_queue(self, chat_id):
        return list(self.music_queue[chat_id])
    
    def pop_song(self, chat_id):
        if self.music_queue[chat_id]:
            return self.music_queue[chat_id].pop(0)
    
    def clear_queue(self, chat_id):
        """Clear queue for a specific chat"""
        if chat_id in self.music_queue:
            count = len(self.music_queue[chat_id])
            self.music_queue[chat_id].clear()
            print(f"🗑️ Cleared queue for chat {chat_id} ({count} songs removed)")
            return count
        return 0
    
    def mark_vc_ended(self, chat_id):
        """Mark voice chat as ended - will auto-clear queue"""
        self.vc_ended_chats.add(chat_id)
        # Clear existing queue immediately
        cleared_count = self.clear_queue(chat_id)
        print(f"🛑 VC ended marked for chat {chat_id}, cleared {cleared_count} pending songs")
    
    def unmark_vc_ended(self, chat_id):
        """Remove VC ended status (when new song is played)"""
        if chat_id in self.vc_ended_chats:
            self.vc_ended_chats.discard(chat_id)
            print(f"✅ VC ended status cleared for chat {chat_id}")
    
    def is_vc_ended(self, chat_id):
        """Check if VC has ended for this chat"""
        return chat_id in self.vc_ended_chats
    
    def get_queue_size(self, chat_id):
        """Get current queue size"""
        return len(self.music_queue[chat_id])
    
    def cleanup_inactive_chats(self, active_chat_ids):
        """Clean up queues for chats that are no longer active"""
        inactive_chats = []
        for chat_id in list(self.music_queue.keys()):
            if chat_id not in active_chat_ids and chat_id not in self.vc_ended_chats:
                # Mark as ended if queue exists but not active
                self.mark_vc_ended(chat_id)
                inactive_chats.append(chat_id)
        return inactive_chats

# Global instance
queue_manager = ChatQueueManager()

# Backward compatibility functions
def add_to_queue(chat_id, item):
    return queue_manager.add_to_queue(chat_id, item)

def get_queue(chat_id):
    return queue_manager.get_queue(chat_id)

def pop_song(chat_id):
    return queue_manager.pop_song(chat_id)

def clear_queue(chat_id):
    return queue_manager.clear_queue(chat_id)
