import asyncio
import os
import re
import logging
import random
from typing import Union
import yt_dlp
import aiohttp
try:
    from pyrogram.enums import MessageEntityType
    from pyrogram.types import Message
except ImportError:
    from hydrogram.enums import MessageEntityType
    from hydrogram.types import Message
try:
    from youtubesearchpython import VideosSearch
except ImportError:
    VideosSearch = None
from urllib.parse import quote

# Logger setup
LOGGER = logging.getLogger("GodVCMusicBot.core.ytdl")

# Codec mapping for format selection
codec_map = {
    'h264': 'vcodec~=(avc1|h264)',
    'av1': 'vcodec~=av01',
    'vp9': 'vcodec~=vp9'
}

# Helper for time formatting
def time_to_seconds(time):
    string_ = str(time)
    return sum(int(x) * 60**i for i, x in enumerate(reversed(string_.split(":"))))

YOUR_API_URL = None
FALLBACK_API_URL = "https://shrutibots.site"
FALLEN_API_URL = "https://fallen-api-v2.vercel.app" # Updated Fallen API

async def load_api_url():
    global YOUR_API_URL
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://pastebin.com/raw/rLsBhAQa", timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    content = await response.text()
                    YOUR_API_URL = content.strip()
                    LOGGER.info(f"✅ Shruti API URL loaded: {YOUR_API_URL}")
                else:
                    YOUR_API_URL = FALLBACK_API_URL
                    LOGGER.info("⚠️ Using fallback Shruti API URL")
    except Exception as e:
        YOUR_API_URL = FALLBACK_API_URL
        LOGGER.info(f"⚠️ Shruti API load failed: {e}. Using fallback.")

# Initialize API URL loading
try:
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.create_task(load_api_url())
    else:
        loop.run_until_complete(load_api_url())
except RuntimeError:
    pass

def get_ydl_opts(proxy=None, format_selection="best", codec_preference="h264"):
    """Get yt-dlp options with robust settings and advanced format selection
    
    Args:
        proxy: Proxy URL (e.g., 'socks5://127.0.0.1:9050')
        format_selection: Quality preference ('best', 'worst', 'ask')
        codec_preference: Codec preference ('h264', 'av1', 'vp9')
    """
    # Build format selector based on codec preference
    # Use proper yt-dlp format selector syntax
    codec_selector = {
        'h264': '[vcodec~="avc1"]+[acodec~="mp4a"]',
        'av1': '[vcodec~="av01"]+[acodec~="mp4a"]',
        'vp9': '[vcodec~="vp9"]+[acodec~="mp4a"]'
    }
    
    preferred_codec = codec_selector.get(codec_preference.lower(), '[vcodec~="avc1"]+[acodec~="mp4a"]')
    
    opts = {
        "format": f"bestaudio*{preferred_codec}/bestaudio/best",
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "extract_flat": False,
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "ios", "web", "mweb", "tv", "web_embedded"],
                "player_skip": ["configs", "webpage"],
                "skip": ["hls", "dash"],
                "po_token": ["web+player"] if not proxy else []  # Use PO token only without proxy
            }
        },
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-us,en;q=0.5",
            "Sec-Fetch-Mode": "navigate",
        },
        "no_check_certificate": True,
        "prefer_ffmpeg": True,
        "ffmpeg_location": "ffmpeg",
        "postprocessors": [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',  # ENHANCED: Maximum quality 320kbps
        }],
        "socket_timeout": 30,
        "retries": 5,
        "fragment_retries": 3,
        "continuedl": True,
        "noresizebuffer": True,
        # ENHANCED: Additional options for better audio quality
        "ffmpeg_options": [
            '-ar', '48000',      # Audio sample rate 48kHz
            '-ac', '2',          # Stereo channels
            '-b:a', '320k',      # Audio bitrate 320kbps
            '-preset', 'ultrafast',  # Fast encoding
            '-fflags', '+genpts',   # Generate timestamps
        ],
    }
    
    # Add PO Token provider if available (from bgutil-provider service)
    po_token_url = os.getenv("PO_TOKEN_URL", "http://localhost:4416")
    if po_token_url and not proxy:
        opts["po_token"] = f"youtube.web+player:{po_token_url}"
    
    # Path to cookies - support multiple cookie files as fallback
    cookie_files = [
        os.path.join(os.getcwd(), "youtube_cookies.txt"),
        os.path.join(os.getcwd(), "cookies", "youtube.txt"),
        "/root/GodVCMusicBot/GodVCMusicBot/youtube_cookies.txt",
        "/root/GodVCMusicBot/cookies/youtube.txt",
    ]
    
    for cookie_path in cookie_files:
        if os.path.exists(cookie_path):
            opts["cookiefile"] = cookie_path
            LOGGER.info(f"🍪 Using cookies from {cookie_path}")
            break
    
    if proxy:
        opts["proxy"] = proxy
        LOGGER.info(f"🌐 Using proxy: {proxy}")
    
    return opts

async def search_fallen_api(query):
    """Search via Fallen API"""
    try:
        LOGGER.info(f"  → Searching via Fallen API: {query}")
        async with aiohttp.ClientSession() as session:
            # Try V2 first
            try:
                async with session.get(f"https://fallen-api-v2.vercel.app/youtube?query={quote(query)}", timeout=15) as response:
                    LOGGER.info(f"  → Fallen API V2 Response Status: {response.status}")
                    if response.status == 200:
                        data = await response.json()
                        if data and isinstance(data, list) and len(data) > 0:
                            song = data[0]
                            LOGGER.info(f"✅ Found via Fallen API V2: {song.get('title')}")
                            return {
                                "title": song.get("title"),
                                "url": song.get("stream_url") or song.get("url"),
                                "thumbnail": song.get("thumbnails")[0] if song.get("thumbnails") else None,
                                "duration": int(song.get("duration", 0)),
                                "webpage_url": song.get("url"),
                                "source": "FallenAPI_V2"
                            }
            except Exception as e:
                LOGGER.error(f"  ❌ Fallen API V2 failed: {e}")
            
            # Try V1 fallback
            try:
                async with session.get(f"https://fallen-api.vercel.app/youtube?query={quote(query)}", timeout=15) as response:
                    LOGGER.info(f"  → Fallen API V1 Response Status: {response.status}")
                    if response.status == 200:
                        data = await response.json()
                        if data and isinstance(data, list) and len(data) > 0:
                            song = data[0]
                            LOGGER.info(f"✅ Found via Fallen API V1: {song.get('title')}")
                            return {
                                "title": song.get("title"),
                                "url": song.get("stream_url") or song.get("url"),
                                "thumbnail": song.get("thumbnails")[0] if song.get("thumbnails") else None,
                                "duration": int(song.get("duration", 0)),
                                "webpage_url": song.get("url"),
                                "source": "FallenAPI_V1"
                            }
            except Exception as e:
                LOGGER.error(f"  ❌ Fallen API V1 failed: {e}")
    except Exception as e:
        LOGGER.error(f"❌ Fallen API Search Process Failed: {e}")
    return None

async def get_available_formats(link: str, codec_preference: str = "h264"):
    """Get available formats for a video with codec information
    
    Args:
        link: YouTube video URL
        codec_preference: Preferred codec ('h264', 'av1', 'vp9')
    
    Returns:
        dict: Available formats grouped by quality and codec
    """
    LOGGER.info(f"📋 Getting available formats for {link}")
    
    try:
        loop = asyncio.get_event_loop()
        def _extract_formats():
            opts = get_ydl_opts(codec_preference=codec_preference)
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(link, download=False)
        
        info = await loop.run_in_executor(None, _extract_formats)
        
        formats_by_quality = {}
        for format in info.get('formats', []):
            # Skip formats without video codec (audio-only for video formats)
            vcodec = format.get('vcodec', 'none')
            acodec = format.get('acodec', 'none')
            height = format.get('height', 0)
            fps = format.get('fps', 30)
            filesize = format.get('filesize') or format.get('filesize_approx')
            tbr = format.get('tbr', 0)  # Total bitrate
            
            # Determine codec type
            codec_type = 'unknown'
            if 'avc1' in vcodec or 'h264' in vcodec.lower():
                codec_type = 'h264'
            elif 'vp9' in vcodec.lower():
                codec_type = 'vp9'
            elif 'av01' in vcodec.lower():
                codec_type = 'av1'
            
            # Skip dash formats (separate audio/video)
            if 'dash' in format.get('format_note', '').lower():
                continue
            
            quality_key = f"{height}p{fps}"
            if quality_key not in formats_by_quality:
                formats_by_quality[quality_key] = {
                    'height': height,
                    'fps': fps,
                    'formats': {},
                    'preference': height  # For sorting
                }
            
            formats_by_quality[quality_key]['formats'][codec_type] = {
                'format_id': format.get('format_id'),
                'ext': format.get('ext', 'mp4'),
                'filesize': filesize,
                'tbr': tbr,
                'vcodec': vcodec,
                'acodec': acodec,
                'url': format.get('url'),
                'format': format.get('format', '')
            }
        
        # Sort by quality (highest first)
        sorted_formats = dict(sorted(
            formats_by_quality.items(),
            key=lambda x: x[1]['preference'],
            reverse=True
        ))
        
        return {
            'success': True,
            'title': info.get('title'),
            'duration': info.get('duration'),
            'thumbnail': info.get('thumbnail'),
            'webpage_url': info.get('webpage_url'),
            'id': info.get('id'),
            'formats': sorted_formats
        }
    except Exception as e:
        LOGGER.error(f"❌ Failed to get formats: {e}")
        return {
            'success': False,
            'error': str(e)
        }

async def download_with_format_selection(link: str, quality: str = "best", codec: str = "h264"):
    """Download video with specific quality and codec selection
    
    Args:
        link: YouTube URL
        quality: Quality preference (e.g., '1080p', '720p', 'best', 'worst')
        codec: Codec preference ('h264', 'av1', 'vp9')
    
    Returns:
        tuple: (file_path, title, duration, thumbnail) or None
    """
    LOGGER.info(f"📥 Downloading with quality={quality}, codec={codec}")
    
    video_id = link.split('v=')[-1].split('&')[0] if 'v=' in link else link
    DOWNLOAD_DIR = "downloads"
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    
    try:
        loop = asyncio.get_event_loop()
        
        def _download():
            # Build format selector
            if quality == "best":
                format_selector = f"bestaudio*[vcodec~=avc1][acodec~=mp4a]/bestaudio/best"
            elif quality == "worst":
                format_selector = f"worstaudio*[vcodec~=avc1][acodec~=mp4a]/worstaudio"
            else:
                # Specific quality like 1080p, 720p
                height = quality.replace('p', '')
                format_selector = f"bestaudio[height<={height}][vcodec~=avc1][acodec~=mp4a]/bestaudio[height<={height}]/best"
            
            opts = get_ydl_opts(codec_preference=codec)
            opts['format'] = format_selector
            opts['outtmpl'] = os.path.join(DOWNLOAD_DIR, f"%(id)s.%(ext)s")
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(link, download=True)
                file_path = ydl.prepare_filename(info)
                # Convert to mp3 if needed with ENHANCED quality settings
                if not file_path.endswith('.mp3'):
                    base_path = os.path.splitext(file_path)[0]
                    mp3_path = f"{base_path}.mp3"
                    if os.path.exists(file_path):
                        # Use ffmpeg to convert with maximum quality
                        import subprocess
                        subprocess.run([
                            'ffmpeg', '-i', file_path,
                            '-vn',           # No video
                            '-acodec', 'libmp3lame',  # LAME encoder (best for MP3)
                            '-b:a', '320k',  # 320kbps bitrate (maximum quality)
                            '-ar', '48000',  # 48kHz sample rate
                            '-ac', '2',      # Stereo
                            '-preset', 'ultrafast',  # Fast encoding
                            '-fflags', '+genpts',   # Generate timestamps
                            '-flags', '+low_delay',  # Low delay
                            mp3_path
                        ], check=True, capture_output=True)
                        return mp3_path, info.get('title'), info.get('duration'), info.get('thumbnail')
                return file_path, info.get('title'), info.get('duration'), info.get('thumbnail')
        
        result = await loop.run_in_executor(None, _download)
        LOGGER.info(f"✅ Downloaded: {result[0]}")
        return result
    except Exception as e:
        LOGGER.error(f"❌ Download failed: {e}")
        return None

async def get_direct_stream_link(link: str, quality: str = "best", codec: str = "h264"):
    """Get direct stream URL without downloading
    
    Args:
        link: YouTube URL
        quality: Quality preference
        codec: Codec preference
    
    Returns:
        str: Direct stream URL
    """
    LOGGER.info(f"🔗 Getting direct stream link for {link}")
    
    try:
        loop = asyncio.get_event_loop()
        def _extract_stream():
            opts = get_ydl_opts(codec_preference=codec)
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(link, download=False)
                return info.get('url'), info.get('title'), info.get('duration'), info.get('thumbnail')
        
        result = await loop.run_in_executor(None, _extract_stream)
        LOGGER.info(f"✅ Got stream link: {result[0][:80]}...")
        return result
    except Exception as e:
        LOGGER.error(f"❌ Failed to get stream link: {e}")
        return None

async def download_song(link: str, quality: str = "best", codec: str = "h264") -> str:
    """Download audio from YouTube with quality and codec selection
    
    Args:
        link: YouTube URL or video ID
        quality: Quality preference ('best', 'worst', or specific like '720p')
        codec: Codec preference ('h264', 'av1', 'vp9')
    
    Returns:
        str: File path if successful, None otherwise
    """
    global YOUR_API_URL
    if not YOUR_API_URL:
        await load_api_url()
        if not YOUR_API_URL:
            YOUR_API_URL = FALLBACK_API_URL
    
    video_id = link.split('v=')[-1].split('&')[0] if 'v=' in link else link
    if not video_id or len(video_id) < 3:
        # If link is not a URL, it might be a query, but we expect a URL here
        if "youtube.com" not in link and "youtu.be" not in link:
            return None
        video_id = link

    DOWNLOAD_DIR = "downloads"
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id.split('/')[-1]}.mp3")

    if os.path.exists(file_path):
        LOGGER.info(f"✅ File already exists: {file_path}")
        return file_path

    # Try advanced download with format selection first
    try:
        LOGGER.info(f"📥 Attempting advanced download (quality=best, codec=h264)")
        result = await download_with_format_selection(link, "best", "h264")
        if result and result[0]:
            downloaded_path = result[0]
            if downloaded_path != file_path and os.path.exists(downloaded_path):
                import shutil
                # Convert to MP3 using ffmpeg with ENHANCED quality
                subprocess_cmd = f'ffmpeg -i "{downloaded_path}" -vn -acodec libmp3lame -b:a 320k -ar 48000 -ac 2 -preset ultrafast -fflags +genpts -flags +low_delay "{file_path}"'
                await shell_cmd(subprocess_cmd)
                if os.path.exists(file_path):
                    try:
                        os.remove(downloaded_path)
                    except:
                        pass
                    LOGGER.info(f"✅ Converted to MP3 (ENHANCED QUALITY): {file_path}")
                    return file_path
            elif os.path.exists(downloaded_path):
                LOGGER.info(f"✅ Downloaded: {downloaded_path}")
                return downloaded_path
    except Exception as e:
        LOGGER.error(f"❌ Advanced download failed: {e}")

    # Try Shruti API first
    try:
        LOGGER.info(f"  → Attempting Shruti API download for {video_id}")
        async with aiohttp.ClientSession() as session:
            params = {"url": video_id, "type": "audio"}
            async with session.get(f"{YOUR_API_URL}/download", params=params, timeout=aiohttp.ClientTimeout(total=60)) as response:
                if response.status == 200:
                    data = await response.json()
                    download_token = data.get("download_token")
                    if download_token:
                        stream_url = f"{YOUR_API_URL}/stream/{video_id}?type=audio"
                        async with session.get(stream_url, headers={"X-Download-Token": download_token}, timeout=aiohttp.ClientTimeout(total=300)) as file_response:
                            if file_response.status == 200:
                                with open(file_path, "wb") as f:
                                    async for chunk in file_response.content.iter_chunked(16384):
                                        f.write(chunk)
                                return file_path
    except Exception as e:
        LOGGER.error(f"  ❌ Shruti API download failed: {e}")

    # Try Fallen API V2 as fallback download
    try:
        LOGGER.info(f"  → Attempting Fallen API V2 download fallback")
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://fallen-api-v2.vercel.app/youtube?query={quote(video_id)}", timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    if data and isinstance(data, list) and len(data) > 0:
                        stream_url = data[0].get("stream_url")
                        if stream_url:
                            async with session.get(stream_url, timeout=aiohttp.ClientTimeout(total=300)) as file_response:
                                if file_response.status == 200:
                                    with open(file_path, "wb") as f:
                                        async for chunk in file_response.content.iter_chunked(16384):
                                            f.write(chunk)
                                    return file_path
    except Exception as e:
        LOGGER.error(f"  ❌ Fallen API download fallback failed: {e}")

    return None

async def download_video(link: str) -> str:
    global YOUR_API_URL
    if not YOUR_API_URL:
        await load_api_url()
        if not YOUR_API_URL:
            YOUR_API_URL = FALLBACK_API_URL
    
    video_id = link.split('v=')[-1].split('&')[0] if 'v=' in link else link
    if not video_id or len(video_id) < 3:
        return None

    DOWNLOAD_DIR = "downloads"
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp4")

    if os.path.exists(file_path):
        return file_path

    try:
        async with aiohttp.ClientSession() as session:
            params = {"url": video_id, "type": "video"}
            async with session.get(f"{YOUR_API_URL}/download", params=params, timeout=aiohttp.ClientTimeout(total=60)) as response:
                if response.status != 200:
                    return None
                data = await response.json()
                download_token = data.get("download_token")
                if not download_token:
                    return None
                
                stream_url = f"{YOUR_API_URL}/stream/{video_id}?type=video"
                async with session.get(stream_url, headers={"X-Download-Token": download_token}, timeout=aiohttp.ClientTimeout(total=600)) as file_response:
                    if file_response.status != 200:
                        return None
                    with open(file_path, "wb") as f:
                        async for chunk in file_response.content.iter_chunked(16384):
                            f.write(chunk)
                    return file_path
    except Exception:
        return None

async def shell_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    out, errorz = await proc.communicate()
    if errorz:
        if "unavailable videos are hidden" in (errorz.decode("utf-8")).lower():
            return out.decode("utf-8")
        else:
            return errorz.decode("utf-8")
    return out.decode("utf-8")

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        return bool(re.search(self.regex, link))

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        for message in messages:
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        return text[entity.offset: entity.offset + entity.length]
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        return None

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        
        # Fallback to direct yt-dlp extraction for details
        try:
            loop = asyncio.get_event_loop()
            def _extract_details():
                with yt_dlp.YoutubeDL(get_ydl_opts()) as ydl:
                    return ydl.extract_info(link, download=False)
            res = await loop.run_in_executor(None, _extract_details)
            return res["title"], str(res.get("duration")), res.get("duration", 0), res.get("thumbnail"), res["id"]
        except Exception as e:
            LOGGER.error(f"  ❌ yt-dlp details extraction failed: {e}")
            raise Exception("No results found")

    async def title(self, link: str, videoid: Union[bool, str] = None):
        title, _, _, _, _ = await self.details(link, videoid)
        return title

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        _, duration_min, _, _, _ = await self.details(link, videoid)
        return duration_min

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        _, _, _, thumb, _ = await self.details(link, videoid)
        return thumb

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        try:
            downloaded_file = await download_video(link)
            if downloaded_file:
                return 1, downloaded_file
            else:
                return 0, "Video download failed"
        except Exception as e:
            return 0, f"Video download error: {e}"

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]
        playlist = await shell_cmd(f"yt-dlp -i --get-id --flat-playlist --playlist-end {limit} --skip-download {link}")
        try:
            result = [key for key in playlist.split("\n") if key]
        except:
            result = []
        return result

    async def track(self, link: str, videoid: Union[bool, str] = None):
        title, duration_min, duration_sec, thumbnail, vidid = await self.details(link, videoid)
        yturl = f"https://www.youtube.com/watch?v={vidid}"
        track_details = {"title": title, "link": yturl, "vidid": vidid, "duration_min": duration_min, "thumb": thumbnail}
        return track_details, vidid

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        
        loop = asyncio.get_event_loop()
        def _extract():
            with yt_dlp.YoutubeDL(get_ydl_opts()) as ydl:
                return ydl.extract_info(link, download=False)
        
        r = await loop.run_in_executor(None, _extract)
        formats_available = []
        for format in r["formats"]:
            try:
                if "dash" not in str(format["format"]).lower():
                    formats_available.append({"format": format["format"], "filesize": format.get("filesize"), "format_id": format["format_id"], "ext": format["ext"], "format_note": format["format_note"], "yturl": link})
            except:
                continue
        return formats_available, link

    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        
        loop = asyncio.get_event_loop()
        def _extract():
            with yt_dlp.YoutubeDL(get_ydl_opts()) as ydl:
                return ydl.extract_info(f"ytsearch10:{link}", download=False)
        
        res_data = await loop.run_in_executor(None, _extract)
        if not res_data.get("entries"):
            raise Exception("No results found")
        
        result = res_data["entries"]
        title = result[query_type]["title"]
        duration_sec = result[query_type]["duration"]
        vidid = result[query_type]["id"]
        thumbnail = result[query_type]["thumbnail"]
        return title, str(duration_sec), thumbnail, vidid

    async def download(self, link: str, mystic, video: Union[bool, str] = None, videoid: Union[bool, str] = None, songaudio: Union[bool, str] = None, songvideo: Union[bool, str] = None, format_id: Union[bool, str] = None, title: Union[bool, str] = None) -> str:
        if videoid:
            link = self.base + link
        try:
            if video:
                downloaded_file = await download_video(link)
            else:
                downloaded_file = await download_song(link)
            if downloaded_file:
                return downloaded_file, True
            else:
                return None, False
        except Exception:
            return None, False

async def resolve_stream(webpage_url):
    """Resolve stream URL with multiple fallbacks including Tor"""
    LOGGER.info(f"🔗 RESOLVING STREAM: {webpage_url}")
    
    # Check if webpage_url is already a stream URL (contains certain keywords)
    if any(k in webpage_url for k in [".googlevideo.com", ".m3u8", ".mp3", ".mp4", "shrutibots.site"]):
        LOGGER.info("  → Already a stream URL, returning as is.")
        return webpage_url

    # Strategy 1: Direct
    try:
        loop = asyncio.get_event_loop()
        def _extract_direct():
            with yt_dlp.YoutubeDL(get_ydl_opts()) as ydl:
                return ydl.extract_info(webpage_url, download=False)["url"]
        return await loop.run_in_executor(None, _extract_direct)
    except Exception as e:
        LOGGER.warning(f"  ❌ Direct resolve failed: {e}")

    # Strategy 2: Tor Fallback
    try:
        LOGGER.info("  → Attempting Tor Fallback for resolve...")
        loop = asyncio.get_event_loop()
        def _extract_tor():
            with yt_dlp.YoutubeDL(get_ydl_opts(proxy="socks5://127.0.0.1:9050")) as ydl:
                return ydl.extract_info(webpage_url, download=False)["url"]
        return await loop.run_in_executor(None, _extract_tor)
    except Exception as e:
        LOGGER.error(f"  ❌ Tor resolve failed: {e}")

    raise Exception("Failed to resolve stream after all attempts")

async def search_youtube(query):
    """Search YouTube using multiple strategies including Fallen API and Tor"""
    LOGGER.info(f"🔍 SEARCHING: {query}")
    
    # 1. Try Fallen API First
    res = await search_fallen_api(query)
    if res: return res

    # 2. Try direct yt-dlp search with cookies
    try:
        LOGGER.info("  → Strategy 2: Direct Search with Cookies")
        loop = asyncio.get_event_loop()
        def _extract_direct():
            # Use specific options for search
            search_opts = get_ydl_opts()
            with yt_dlp.YoutubeDL(search_opts) as ydl:
                return ydl.extract_info(f"ytsearch1:{query}", download=False)["entries"][0]
        
        res = await loop.run_in_executor(None, _extract_direct)
        if res:
            LOGGER.info(f"✅ Found via Strategy 2: {res.get('title')}")
            return {
                "title": res["title"], 
                "url": res.get("url"), 
                "thumbnail": res.get("thumbnail"), 
                "webpage_url": res.get("webpage_url"), 
                "duration": res.get("duration"), 
                "vidid": res.get("id")
            }
    except Exception as e:
        LOGGER.warning(f"  ❌ Strategy 2 failed: {e}")

    # 3. Tor Fallback for Search
    try:
        LOGGER.info("  → Strategy 3: Search with Tor")
        loop = asyncio.get_event_loop()
        def _extract_tor():
            tor_opts = get_ydl_opts(proxy="socks5://127.0.0.1:9050")
            with yt_dlp.YoutubeDL(tor_opts) as ydl:
                return ydl.extract_info(f"ytsearch1:{query}", download=False)["entries"][0]
        
        res = await loop.run_in_executor(None, _extract_tor)
        if res:
            LOGGER.info(f"✅ Found via Strategy 3 (Tor): {res.get('title')}")
            return {
                "title": res["title"], 
                "url": res.get("url"), 
                "thumbnail": res.get("thumbnail"), 
                "webpage_url": res.get("webpage_url"), 
                "duration": res.get("duration"), 
                "vidid": res.get("id")
            }
    except Exception as e:
        LOGGER.error(f"  ❌ Tor search failed: {e}")

    # 4. Try youtubesearchpython (very light, often not blocked)
    try:
        LOGGER.info("  → Strategy 4: youtubesearchpython")
        from youtubesearchpython import VideosSearch
        search = VideosSearch(query, limit=1)
        result = search.result()
        if result and result.get("result"):
            res = result["result"][0]
            LOGGER.info(f"✅ Found via Strategy 4: {res.get('title')}")
            return {
                "title": res["title"],
                "url": None, 
                "thumbnail": res["thumbnails"][0]["url"] if res.get("thumbnails") else None,
                "webpage_url": res["link"],
                "duration": time_to_seconds(res.get("duration")),
                "vidid": res.get("id")
            }
    except Exception as e:
        LOGGER.error(f"  ❌ Strategy 4 failed: {e}")

    # 5. Final attempt: PyTube search as a last resort
    try:
        LOGGER.info("  → Strategy 5: PyTube Search")
        from pytube import Search
        s = Search(query)
        if s.results:
            res = s.results[0]
            LOGGER.info(f"✅ Found via Strategy 5: {res.title}")
            return {
                "title": res.title,
                "url": None,
                "thumbnail": res.thumbnail_url,
                "webpage_url": res.watch_url,
                "duration": res.length,
                "vidid": res.video_id
            }
    except Exception as e:
        LOGGER.error(f"  ❌ Strategy 5 failed: {e}")

    raise Exception("All search strategies failed. YouTube is blocking the server.")

async def search_youtube_video(query):
    return await search_youtube(query)
