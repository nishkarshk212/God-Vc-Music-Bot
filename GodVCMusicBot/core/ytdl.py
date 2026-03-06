import yt_dlp
import os

def get_ydl_opts():
    """Get yt-dlp options with cookie support"""
    opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "no_warnings": True,
        "extractor_args": {"youtube": {"player_client": ["ios"]}}
    }
    
    # Check for cookies file in multiple locations (including absolute paths)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    home_dir = os.path.expanduser("~")
    
    cookie_paths = [
        os.path.join(script_dir, "youtube_cookies.txt"),
        os.path.join(home_dir, "GodVCMusicBot", "GodVCMusicBot", "youtube_cookies.txt"),
        os.path.join(home_dir, "GodVCMusicBot", "youtube_cookies.txt"),
        "/root/GodVCMusicBot/GodVCMusicBot/youtube_cookies.txt",
        "youtube_cookies.txt",
        "GodVCMusicBot/youtube_cookies.txt"
    ]
    
    for cookie_path in cookie_paths:
        if os.path.exists(cookie_path):
            opts["cookiefile"] = cookie_path
            print(f"✅ Using cookies from: {cookie_path}")
            break
    
    return opts

def search_youtube(query):
    ydl_opts = get_ydl_opts()
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(f"ytsearch:{query}", download=False)["entries"][0]
    return {
        "title": result.get("title"),
        "url": result.get("url"),
        "thumbnail": result.get("thumbnail"),
        "webpage_url": result.get("webpage_url"),
        "duration": result.get("duration"),
    }

def search_youtube_video(query):
    ydl_opts = get_ydl_opts()
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(f"ytsearch:{query}", download=False)["entries"][0]
    return {
        "title": result.get("title"),
        "url": result.get("url"),
        "thumbnail": result.get("thumbnail"),
        "webpage_url": result.get("webpage_url"),
        "duration": result.get("duration"),
    }

def resolve_stream(webpage_url):
    ydl_opts = get_ydl_opts()
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(webpage_url, download=False)
        return info.get("url")
