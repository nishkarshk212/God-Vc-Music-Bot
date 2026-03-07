import yt_dlp
import os

def get_ydl_opts():
    """Get yt-dlp options with cookie support"""
    opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "no_warnings": True,
        "extractor_args": {
            "youtube": {
                "player_client": ["web", "ios"],
                "skip": ["hls"]
            }
        },
        "no_check_certificate": True
    }
    
    # Check for cookies file
    cookie_path = "/root/GodVCMusicBot/GodVCMusicBot/youtube_cookies.txt"
    if os.path.exists(cookie_path):
        opts["cookiefile"] = cookie_path
        print(f"✅ Using cookies from: {cookie_path}")
    
    return opts

def search_youtube(query):
    ydl_opts = get_ydl_opts()
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(f"ytsearch:{query}", download=False)["entries"][0]
        return {
            "title": result.get("title"),
            "url": result.get("url"),
            "thumbnail": result.get("thumbnail"),
            "webpage_url": result.get("webpage_url"),
            "duration": result.get("duration"),
        }
    except Exception as e:
        print(f"Error in search_youtube: {e}")
        raise

def search_youtube_video(query):
    return search_youtube(query)

def resolve_stream(webpage_url):
    ydl_opts = get_ydl_opts()
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(webpage_url, download=False)
            return info.get("url")
    except Exception as e:
        print(f"Error in resolve_stream: {e}")
        raise
