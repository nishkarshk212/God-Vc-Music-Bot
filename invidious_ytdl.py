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

def get_ydl_opts():
    """Get yt-dlp options - tries Invidious first, then YouTube with multiple strategies"""
    
    # Randomly select an Invidious instance
    invidious_instance = random.choice(INVIDIOUS_INSTANCES)
    
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
        # Use Invidious instance
        "invidious": invidious_instance
    }
    
    return opts, invidious_instance

def search_youtube(query):
    """Search YouTube using Invidious or direct with fallback strategies"""
    
    print(f"🔍 Searching: {query}")
    
    # Strategy 1: Try Invidious (no auth needed)
    try:
        opts, instance = get_ydl_opts()
        print(f"  → Trying Invidious instance: {instance}")
        
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
        print(f"  ❌ Invidious failed: {str(e)[:80]}")
    
    # Strategy 2-5: Try direct YouTube with different clients (fallback)
    strategies = [
        {"clients": ["web", "android"], "use_cookies": False},
        {"clients": ["ios"], "use_cookies": False},
        {"clients": ["tv"], "use_cookies": False},
        {"clients": ["web"], "use_cookies": False}
    ]
    
    for strategy in strategies:
        try:
            print(f"  → Trying {strategy['clients']} client (no cookies)")
            opts = {
                "format": "bestaudio[ext=m4a]/bestaudio/best",
                "quiet": True,
                "no_warnings": True,
                "extractor_args": {
                    "youtube": {
                        "player_client": strategy['clients'],
                        "skip": ["hls"]
                    }
                },
                "no_check_certificate": True
            }
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                result = ydl.extract_info(f"ytsearch:{query}", download=False)["entries"][0]
            
            print(f"  ✅ Success via direct YouTube!")
            return {
                "title": result.get("title"),
                "url": result.get("url"),
                "thumbnail": result.get("thumbnail"),
                "webpage_url": result.get("webpage_url"),
                "duration": result.get("duration"),
            }
        except Exception as e:
            print(f"  ❌ Failed: {str(e)[:80]}")
    
    raise Exception("All search strategies failed")

def search_youtube_video(query):
    return search_youtube(query)

def resolve_stream(webpage_url):
    """Resolve stream URL using Invidious or direct"""
    
    # Try Invidious first
    try:
        opts, instance = get_ydl_opts()
        print(f"  → Resolving via Invidious: {instance}")
        
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(webpage_url, download=False)
            return info.get("url")
    except Exception as e:
        print(f"  ❌ Invidious failed: {str(e)[:80]}")
    
    # Try direct YouTube without cookies
    strategies = [
        {"clients": ["web", "android"]},
        {"clients": ["ios"]},
        {"clients": ["tv"]}
    ]
    
    for strategy in strategies:
        try:
            print(f"  → Resolving via {strategy['clients']} client")
            opts = {
                "format": "bestaudio[ext=m4a]/bestaudio/best",
                "quiet": True,
                "no_warnings": True,
                "extractor_args": {
                    "youtube": {
                        "player_client": strategy['clients'],
                        "skip": ["hls"]
                    }
                },
                "no_check_certificate": True
            }
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(webpage_url, download=False)
                return info.get("url")
        except Exception as e:
            print(f"  ❌ Failed: {str(e)[:80]}")
    
    raise Exception("All resolution strategies failed")
