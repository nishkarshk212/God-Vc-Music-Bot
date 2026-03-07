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

def get_ydl_opts(proxy=None, use_invidious=None, clients=None):
    """Get yt-dlp options with optional proxy, Invidious, and client support"""
    
    if clients is None:
        clients = ["android"]
    
    opts = {
        "format": "bestaudio[ext=m4a]/bestaudio/best",
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "extractor_args": {
            "youtube": {
                "player_client": clients,
                "player_skip": ["configs"],
                "skip": ["hls"]
            }
        },
        "http_headers": {
            "User-Agent": "com.google.android.youtube/19.29.37 (Linux; U; Android 13)"
        },
        "no_check_certificate": True,
        "socket_timeout": 15,
        "retries": 2
    }
    
    if proxy:
        opts["proxy"] = proxy
        print(f"  🌐 Using proxy: {proxy}")
    
    if use_invidious:
        opts["invidious"] = use_invidious
        print(f"  🔄 Using Invidious instance: {use_invidious}")
    
    return opts

def search_youtube(query):
    """Search YouTube using Invidious + Android client fallback"""
    
    print(f"\n🔍 Searching for: {query}")
    
    # Strategy 1: Try ALL Invidious instances first (most reliable)
    shuffled_instances = INVIDIOUS_INSTANCES.copy()
    random.shuffle(shuffled_instances)
    
    for i, instance in enumerate(shuffled_instances, start=1):
        try:
            print(f"  → Attempt {i}: Invidious ({instance})")
            opts = get_ydl_opts(use_invidious=instance, clients=["android"])
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                result = ydl.extract_info(f"ytsearch1:{query}", download=False)["entries"][0]
            
            print(f"  ✅ Success via Invidious!")
            
            # Get direct stream URL
            direct_url = result.get("url")
            
            # If it's a webpage URL, extract the direct stream
            if "youtube.com" in direct_url or "youtu.be" in direct_url:
                print(f"  🔄 Extracting direct stream URL...")
                stream_info = ydl.extract_info(direct_url, download=False)
                direct_url = stream_info.get("url")
            
            return {
                "title": result.get("title"),
                "url": direct_url,
                "thumbnail": result.get("thumbnail"),
                "webpage_url": result.get("webpage_url"),
                "duration": result.get("duration"),
            }
        except Exception as e:
            error_msg = str(e)
            if "Sign in to confirm" in error_msg or "bot" in error_msg.lower():
                print(f"  ❌ Blocked by YouTube (trying next Invidious)")
            else:
                print(f"  ❌ Failed: {str(error_msg)[:50]}")
            continue
    
    # Strategy 2: Try with cookies + Android client
    cookie_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "youtube_cookies.txt"),
        os.path.join(os.path.expanduser("~"), "GodVCMusicBot", "youtube_cookies.txt"),
        "/root/GodVCMusicBot/youtube_cookies.txt",
        "youtube_cookies.txt"
    ]
    
    for cookie_path in cookie_paths:
        if os.path.exists(cookie_path):
            try:
                print(f"  → Attempting with cookies from: {cookie_path}")
                opts = get_ydl_opts(clients=["android"])
                opts["cookiefile"] = cookie_path
                
                with yt_dlp.YoutubeDL(opts) as ydl:
                    result = ydl.extract_info(f"ytsearch1:{query}", download=False)["entries"][0]
                
                print(f"  ✅ Success with cookies!")
                
                # Get direct stream URL
                direct_url = result.get("url")
                
                # If it's a webpage URL, extract the direct stream
                if "youtube.com" in direct_url or "youtu.be" in direct_url:
                    print(f"  🔄 Extracting direct stream URL...")
                    stream_info = ydl.extract_info(direct_url, download=False)
                    direct_url = stream_info.get("url")
                
                return {
                    "title": result.get("title"),
                    "url": direct_url,
                    "thumbnail": result.get("thumbnail"),
                    "webpage_url": result.get("webpage_url"),
                    "duration": result.get("duration"),
                }
            except Exception as e:
                print(f"  ❌ Cookie method failed: {str(e)[:50]}")
                continue
    
    # Strategy 3: Direct YouTube with Android client (last resort)
    try:
        print(f"  → Last attempt: Direct YouTube (Android client)")
        opts = get_ydl_opts(clients=["android"])
        
        with yt_dlp.YoutubeDL(opts) as ydl:
            result = ydl.extract_info(f"ytsearch1:{query}", download=False)["entries"][0]
        
        print(f"  ✅ Success via direct!")
        
        # Get direct stream URL
        direct_url = result.get("url")
        
        # If it's a webpage URL, extract the direct stream
        if "youtube.com" in direct_url or "youtu.be" in direct_url:
            print(f"  🔄 Extracting direct stream URL...")
            stream_info = ydl.extract_info(direct_url, download=False)
            direct_url = stream_info.get("url")
        
        return {
            "title": result.get("title"),
            "url": direct_url,
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
    """Resolve stream URL using Invidious + direct fallback"""
    
    print(f"\n🔗 Resolving stream URL: {webpage_url[:60]}...")
    
    # Try Invidious first
    shuffled_instances = INVIDIOUS_INSTANCES[:3].copy()
    random.shuffle(shuffled_instances)
    
    for instance in shuffled_instances:
        try:
            print(f"  → Resolving via Invidious ({instance})...")
            opts = get_ydl_opts(use_invidious=instance)
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(webpage_url, download=False)
                stream_url = info.get("url")
            
            print(f"  ✅ Successfully resolved via Invidious!")
            return stream_url
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
