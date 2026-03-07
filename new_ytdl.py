import yt_dlp
import os

def get_ydl_opts(use_cookies=True):
    """Get yt-dlp options - tries multiple client approaches"""
    opts = {
        "format": "bestaudio[ext=m4a]/bestaudio/best",
        "quiet": True,
        "no_warnings": True,
        "extractor_args": {
            "youtube": {
                "player_client": ["web", "android", "ios"],
                "skip": ["hls"]
            }
        },
        "no_check_certificate": True
    }
    
    if use_cookies:
        # Check for cookies file
        cookie_path = "/root/GodVCMusicBot/GodVCMusicBot/youtube_cookies.txt"
        if os.path.exists(cookie_path):
            opts["cookiefile"] = cookie_path
            print(f"ℹ️  Using cookies (attempting auth)")
    
    return opts

def search_youtube(query):
    """Search YouTube with fallback strategies"""
    
    # Strategy 1: Try with web client + cookies
    print(f"🔍 Searching: {query}")
    
    strategies = [
        {"use_cookies": True, "clients": ["web", "android"]},
        {"use_cookies": False, "clients": ["web", "android"]},
        {"use_cookies": True, "clients": ["ios"]},
        {"use_cookies": False, "clients": ["ios"]}
    ]
    
    for strategy in strategies:
        try:
            print(f"  → Trying {strategy['clients']} client, cookies={strategy['use_cookies']}")
            opts = get_ydl_opts(use_cookies=strategy['use_cookies'])
            opts["extractor_args"]["youtube"]["player_client"] = strategy['clients']
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                result = ydl.extract_info(f"ytsearch:{query}", download=False)["entries"][0]
            
            print(f"  ✅ Success!")
            return {
                "title": result.get("title"),
                "url": result.get("url"),
                "thumbnail": result.get("thumbnail"),
                "webpage_url": result.get("webpage_url"),
                "duration": result.get("duration"),
            }
        except Exception as e:
            error_msg = str(e)
            print(f"  ❌ Failed: {error_msg[:80]}")
            if "Sign in" not in error_msg and "format is not available" not in error_msg:
                # Some other error, might be worth retrying
                continue
    
    raise Exception("All strategies failed")

def search_youtube_video(query):
    return search_youtube(query)

def resolve_stream(webpage_url):
    """Resolve stream URL with fallback strategies"""
    
    strategies = [
        {"use_cookies": True, "clients": ["web", "android"]},
        {"use_cookies": False, "clients": ["web", "android"]},
        {"use_cookies": True, "clients": ["ios"]},
        {"use_cookies": False, "clients": ["ios"]}
    ]
    
    for strategy in strategies:
        try:
            print(f"  → Resolving with {strategy['clients']} client, cookies={strategy['use_cookies']}")
            opts = get_ydl_opts(use_cookies=strategy['use_cookies'])
            opts["extractor_args"]["youtube"]["player_client"] = strategy['clients']
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(webpage_url, download=False)
                return info.get("url")
        except Exception as e:
            error_msg = str(e)
            print(f"  ❌ Failed: {error_msg[:80]}")
            if "Sign in" not in error_msg and "format is not available" not in error_msg:
                continue
    
    raise Exception("All strategies failed to resolve stream")
