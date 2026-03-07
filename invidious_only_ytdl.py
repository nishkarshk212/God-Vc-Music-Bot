import yt_dlp
import os
import random

# List of Invidious instances (alternative YouTube frontends)
INVIDIOUS_INSTANCES = [
    "https://invidious.io.lol",
    "https://invidious.fdn.fr",
    "https://yewtu.be",
    "https://inv.riverside.rocks",
    "https://invidious.blamefran.net",
]

def get_ydl_opts(proxy=None):
    """Get yt-dlp options with optional proxy support"""
    
    opts = {
        "format": "bestaudio[ext=m4a]/bestaudio/best",
        "quiet": True,
        "no_warnings": True,
        "extractor_args": {
            "youtube": {
                "player_client": ["web", "android"],
                "skip": ["hls"]
            }
        },
        "no_check_certificate": True,
        "socket_timeout": 10,
        "retries": 1
    }
    
    if proxy:
        opts["proxy"] = proxy
        print(f"  🌐 Using proxy: {proxy}")
    
    return opts

def search_youtube(query):
    """Search YouTube using direct connection + Invidious fallback"""
    
    print(f"🔍 Searching: {query}")
    
    # Strategy 1: Try ALL Invidious instances first (most reliable)
    random.shuffle(INVIDIOUS_INSTANCES)
    for i, instance in enumerate(INVIDIOUS_INSTANCES, start=1):
        try:
            print(f"  → Attempt {i}: Invidious ({instance})")
            opts = get_ydl_opts()
            opts["invidious"] = instance
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                result = ydl.extract_info(f"ytsearch:{query}", download=False)["entries"][0]
            
            print(f"  ✅ Success via Invidious!")
            return {
                "title": result.get("title"),
                "url": result.get("url"),
                "thumbnail": result.get("thumbnail"),
                "webpage_url": result.get("webpage_url"),
                "duration": result.get("duration"),
            }
        except Exception as e:
            error_msg = str(e)
            if "Sign in to confirm" in error_msg or "bot" in error_msg.lower():
                print(f"  ❌ Blocked by YouTube (trying next Invidious)")
            else:
                print(f"  ❌ Failed: {str(e)[:50]}")
            continue
    
    # Strategy 2: Direct YouTube (last resort, usually blocked)
    try:
        print(f"  → Last attempt: Direct YouTube")
        opts = get_ydl_opts()
        
        with yt_dlp.YoutubeDL(opts) as ydl:
            result = ydl.extract_info(f"ytsearch:{query}", download=False)["entries"][0]
        
        print(f"  ✅ Success via direct!")
        return {
            "title": result.get("title"),
            "url": result.get("url"),
            "thumbnail": result.get("thumbnail"),
            "webpage_url": result.get("webpage_url"),
            "duration": result.get("duration"),
        }
    except Exception as e:
        print(f"  ❌ Direct failed: {str(e)[:80]}")
    
    raise Exception("All strategies failed - YouTube is blocking this server IP")

def search_youtube_video(query):
    return search_youtube(query)

def resolve_stream(webpage_url):
    """Resolve stream URL"""
    
    # Try Invidious first
    for instance in INVIDIOUS_INSTANCES[:3]:
        try:
            print(f"  → Resolving via Invidious...")
            opts = get_ydl_opts()
            opts["invidious"] = instance
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(webpage_url, download=False)
                return info.get("url")
        except Exception as e:
            print(f"  ❌ Invidious failed: {str(e)[:50]}")
            continue
    
    # Try direct
    try:
        print(f"  → Resolving directly...")
        opts = get_ydl_opts()
        
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(webpage_url, download=False)
            return info.get("url")
    except Exception as e:
        print(f"  ❌ Direct failed: {str(e)[:50]}")
    
    raise Exception("Failed to resolve stream")
