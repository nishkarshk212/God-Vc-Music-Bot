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

# Free proxy list (rotate through these)
FREE_PROXIES = [
    # HTTP proxies
    "http://proxy1.example.com:8080",  # Replace with working proxies
    "http://proxy2.example.com:8080",
    # We'll try without proxy first, then with proxies
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
        "no_check_certificate": True
    }
    
    # Add proxy if provided
    if proxy:
        opts["proxy"] = proxy
        print(f"  🌐 Using proxy: {proxy}")
    
    return opts

def search_youtube(query):
    """Search YouTube using multiple strategies including proxies"""
    
    print(f"🔍 Searching: {query}")
    
    # Strategy 1: Try WITHOUT proxy first (might work if IP isn't blocked)
    try:
        print(f"  → Attempt 1: Direct connection (no proxy)")
        opts = get_ydl_opts()
        
        with yt_dlp.YoutubeDL(opts) as ydl:
            result = ydl.extract_info(f"ytsearch:{query}", download=False)["entries"][0]
        
        print(f"  ✅ Success via direct connection!")
        return {
            "title": result.get("title"),
            "url": result.get("url"),
            "thumbnail": result.get("thumbnail"),
            "webpage_url": result.get("webpage_url"),
            "duration": result.get("duration"),
        }
    except Exception as e:
        print(f"  ❌ Direct failed: {str(e)[:80]}")
    
    # Strategy 2-6: Try with different free proxies
    proxy_list = [
        "http://47.88.29.55:8080",
        "http://103.152.112.162:80",
        "http://185.217.136.28:1337",
        "http://20.206.106.216:80",
        "http://103.167.135.110:80",
    ]
    
    for i, proxy in enumerate(proxy_list, start=2):
        try:
            print(f"  → Attempt {i}: Trying proxy {proxy}")
            opts = get_ydl_opts(proxy=proxy)
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                result = ydl.extract_info(f"ytsearch:{query}", download=False)["entries"][0]
            
            print(f"  ✅ Success via proxy!")
            return {
                "title": result.get("title"),
                "url": result.get("url"),
                "thumbnail": result.get("thumbnail"),
                "webpage_url": result.get("webpage_url"),
                "duration": result.get("duration"),
            }
        except Exception as e:
            print(f"  ❌ Proxy failed: {str(e)[:60]}")
            continue
    
    # Strategy 7-11: Try Invidious instances (last resort)
    for instance in INVIDIOUS_INSTANCES:
        try:
            print(f"  → Trying Invidious: {instance}")
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
            print(f"  ❌ Invidious failed: {str(e)[:60]}")
            continue
    
    raise Exception("All strategies (direct + proxies + Invidious) failed")

def search_youtube_video(query):
    return search_youtube(query)

def resolve_stream(webpage_url):
    """Resolve stream URL with proxy support"""
    
    # Try direct first
    try:
        print(f"  → Resolving directly...")
        opts = get_ydl_opts()
        
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(webpage_url, download=False)
            return info.get("url")
    except Exception as e:
        print(f"  ❌ Direct failed: {str(e)[:60]}")
    
    # Try with proxies
    proxy_list = [
        "http://47.88.29.55:8080",
        "http://103.152.112.162:80",
        "http://185.217.136.28:1337",
    ]
    
    for proxy in proxy_list:
        try:
            print(f"  → Trying proxy: {proxy}")
            opts = get_ydl_opts(proxy=proxy)
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(webpage_url, download=False)
                return info.get("url")
        except Exception as e:
            print(f"  ❌ Proxy failed: {str(e)[:60]}")
            continue
    
    raise Exception("Failed to resolve stream")
