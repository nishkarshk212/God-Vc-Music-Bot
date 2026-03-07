import yt_dlp
import os

def get_ydl_opts(use_cookies=True, clients=None):
    """Get yt-dlp options with configurable client and cookies"""
    
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
        "no_check_certificate": True
    }

    cookie_path = "/root/GodVCMusicBot/GodVCMusicBot/youtube_cookies.txt"

    if use_cookies and os.path.exists(cookie_path):
        opts["cookiefile"] = cookie_path
        print("🍪 Using YouTube cookies")

    return opts

def search_youtube(query):
    """Search YouTube with multiple client strategies"""
    
    print(f"🔍 Searching: {query}")
    
    # Try different client strategies in order of preference
    strategies = [
        {"use_cookies": True, "clients": ["android"]},
        {"use_cookies": False, "clients": ["android"]},
        {"use_cookies": True, "clients": ["ios"]},
        {"use_cookies": False, "clients": ["ios"]},
    ]
    
    for strategy in strategies:
        try:
            print(f"  → Trying {strategy['clients']} client, cookies={strategy['use_cookies']}")
            opts = get_ydl_opts(use_cookies=strategy['use_cookies'], clients=strategy['clients'])
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                result = ydl.extract_info(f"ytsearch1:{query}", download=False)["entries"][0]
            
            print(f"  ✅ Success!")
            
            # Get direct stream URL
            direct_url = result.get("url")
            
            # If it's a webpage URL, extract the direct stream
            if "youtube.com" in direct_url or "youtu.be" in direct_url:
                print(f"  🔄 Extracting direct stream URL...")
                stream_opts = get_ydl_opts(use_cookies=strategy['use_cookies'], clients=strategy['clients'])
                with yt_dlp.YoutubeDL(stream_opts) as ydl:
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
            print(f"  ❌ Failed: {error_msg[:80]}")
            # Continue to next strategy
            continue
    
    raise Exception("All strategies failed - YouTube is blocking this server IP")

def search_youtube_video(query):
    return search_youtube(query)

def resolve_stream(webpage_url):
    """Resolve stream URL with multiple client strategies"""
    
    print(f"🔗 Resolving: {webpage_url[:60]}...")
    
    strategies = [
        {"use_cookies": True, "clients": ["android"]},
        {"use_cookies": False, "clients": ["android"]},
        {"use_cookies": True, "clients": ["ios"]},
        {"use_cookies": False, "clients": ["ios"]},
    ]
    
    for strategy in strategies:
        try:
            print(f"  → Using {strategy['clients']} client, cookies={strategy['use_cookies']}")
            opts = get_ydl_opts(use_cookies=strategy['use_cookies'], clients=strategy['clients'])
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(webpage_url, download=False)
                return info.get("url")
        except Exception as e:
            error_msg = str(e)
            print(f"  ❌ Failed: {error_msg[:80]}")
            continue
    
    raise Exception("All strategies failed to resolve stream")
