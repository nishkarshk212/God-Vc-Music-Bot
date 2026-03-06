import yt_dlp

def search_youtube(query):
    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "no_warnings": True,
        "extractor_args": {"youtube": {"player_client": ["ios"]}}
    }
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
    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "quiet": True,
        "no_warnings": True,
        "extractor_args": {"youtube": {"player_client": ["ios"]}}
    }
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
    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "no_warnings": True,
        "extractor_args": {"youtube": {"player_client": ["ios"]}}
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(webpage_url, download=False)
        return info.get("url")
