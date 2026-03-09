import asyncio
import os
import re
import logging
import random
from typing import Union, Optional, Dict, Any, List
import yt_dlp
import aiohttp
import pytube
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
    # Rotation logic for User-Agent
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36"
    ]
    
    opts = {
        "format": "ba[ext=m4a]/ba/b",
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "extract_flat": False,
        "check_formats": False, # Faster and avoids some "format not available" errors
        "ignoreerrors": True, 
        "no_color": True,
        "geo_bypass": True,
        "geo_bypass_country": "US",
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "ios", "mweb", "tv"],
                "player_skip": ["configs", "webpage"],
                "skip": ["hls", "dash"],
            }
        },
        "http_headers": {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Sec-Fetch-Mode": "navigate",
            "Origin": "https://www.youtube.com",
            "Referer": "https://www.youtube.com/",
        },
        "no_check_certificate": True,
        "prefer_ffmpeg": True,
        "ffmpeg_location": "ffmpeg",
        "postprocessors": [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '128',
        }],
        "socket_timeout": 30,
        "retries": 10,
        "fragment_retries": 10,
        "continuedl": True,
        "noresizebuffer": True,
        "concurrent_fragment_downloads": 5,
        "ffmpeg_options": [
            '-ar', '48000',
            '-ac', '2',
            '-b:a', '128k',
            '-preset', 'ultrafast',
            '-fflags', '+genpts',
            '-bufsize', '1000k',
        ],
    }
    
    po_token_url = os.getenv("PO_TOKEN_URL", "http://localhost:4416")
    if po_token_url and not proxy:
        opts["po_token"] = f"youtube.web+player:{po_token_url}"
    
    cookie_files = [
        os.path.join(os.getcwd(), "cookies (3).txt"),
        os.path.join(os.getcwd(), "youtube_cookies.txt"),
        os.path.join(os.getcwd(), "cookies", "youtube.txt"),
        "/root/GodVCMusicBot/cookies (3).txt",
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

# Fallen APIs
FALLEN_API_V2 = "https://fallen-api-v2.vercel.app"
FALLEN_API_V1 = "https://fallen-api.vercel.app"

# Invidious Instances for Fallback Search
INVIDIOUS_INSTANCES = [
    "https://invidious.snopyta.org",
    "https://yewtu.be",
    "https://invidious.kavin.rocks",
    "https://vid.puffyan.us",
    "https://invidious.namazso.eu",
    "https://inv.riverside.rocks",
    "https://invidious.osi.kr",
    "https://youtube.076.ne.jp",
    "https://yt.artemislena.eu",
    "https://invidious.mutatux.org"
]

async def search_invidious(query):
    """Search via Invidious API as a robust fallback"""
    LOGGER.info(f"🔍 Searching Invidious fallback for: {query}")
    async with aiohttp.ClientSession() as session:
        random.shuffle(INVIDIOUS_INSTANCES)
        for instance in INVIDIOUS_INSTANCES[:3]:
            try:
                search_url = f"{instance}/api/v1/search?q={quote(query)}&type=video"
                async with session.get(search_url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data and len(data) > 0:
                            video = data[0]
                            LOGGER.info(f"✅ Found via Invidious ({instance}): {video.get('title')}")
                            return {
                                "title": video.get("title"),
                                "url": None,
                                "thumbnail": video.get("videoThumbnails", [{}])[0].get("url"),
                                "duration": int(video.get("lengthSeconds", 0)),
                                "webpage_url": f"https://www.youtube.com/watch?v={video.get('videoId')}",
                                "vidid": video.get("videoId"),
                                "source": f"Invidious ({instance})"
                            }
            except Exception as e:
                LOGGER.warning(f"  ❌ Invidious ({instance}) failed: {e}")
    return None

async def search_fallen_api(query):
    """Search via Fallen API"""
    try:
        LOGGER.info(f"  → Searching via Fallen API: {query}")
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{FALLEN_API_V2}/youtube?query={quote(query)}", timeout=15) as response:
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
                                "vidid": song.get("id") or (song.get("url", "").split("v=")[-1] if "v=" in song.get("url", "") else None),
                                "source": "FallenAPI_V2"
                            }
            except Exception:
                pass
            
            try:
                async with session.get(f"{FALLEN_API_V1}/youtube?query={quote(query)}", timeout=15) as response:
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
                                "vidid": song.get("id") or (song.get("url", "").split("v=")[-1] if "v=" in song.get("url", "") else None),
                                "source": "FallenAPI_V1"
                            }
            except Exception:
                pass
    except Exception as e:
        LOGGER.error(f"❌ Fallen API Search Process Failed: {e}")
    return None

async def get_available_formats(link: str, codec_preference: str = "h264"):
    """Get available formats for a video with codec information"""
    LOGGER.info(f"📋 Getting available formats for {link}")
    try:
        loop = asyncio.get_event_loop()
        def _extract_formats():
            opts = get_ydl_opts(codec_preference=codec_preference)
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(link, download=False)
                if not info:
                    return None
                return info
        info = await loop.run_in_executor(None, _extract_formats)
        if not info:
            return {'success': False, 'error': "Extraction returned no info"}
        formats_by_quality = {}
        for format in info.get('formats', []):
            vcodec = format.get('vcodec', 'none')
            acodec = format.get('acodec', 'none')
            height = format.get('height', 0)
            fps = format.get('fps', 30)
            filesize = format.get('filesize') or format.get('filesize_approx')
            tbr = format.get('tbr', 0)
            codec_type = 'unknown'
            if 'avc1' in vcodec or 'h264' in vcodec.lower():
                codec_type = 'h264'
            elif 'vp9' in vcodec.lower():
                codec_type = 'vp9'
            elif 'av01' in vcodec.lower():
                codec_type = 'av1'
            if 'dash' in format.get('format_note', '').lower():
                continue
            quality_key = f"{height}p{fps}"
            if quality_key not in formats_by_quality:
                formats_by_quality[quality_key] = {
                    'height': height,
                    'fps': fps,
                    'formats': {},
                    'preference': height
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
        sorted_formats = dict(sorted(formats_by_quality.items(), key=lambda x: x[1]['preference'], reverse=True))
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
        return {'success': False, 'error': str(e)}

async def download_with_format_selection(link: str, quality: str = "best", codec: str = "h264"):
    """Download video with specific quality and codec selection"""
    LOGGER.info(f"📥 Downloading with quality={quality}, codec={codec}")
    DOWNLOAD_DIR = "downloads"
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    try:
        loop = asyncio.get_event_loop()
        def _download():
            format_selector = "ba[ext=m4a]/ba/b"
            opts = get_ydl_opts(codec_preference=codec)
            opts['format'] = format_selector
            opts['outtmpl'] = os.path.join(DOWNLOAD_DIR, f"%(id)s.%(ext)s")
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(link, download=True)
                if not info:
                    raise Exception("yt-dlp returned no info during download")
                file_path = ydl.prepare_filename(info)
                
                # Double check if file exists and is non-empty
                if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
                    # Try to find any file with the same ID in the directory as fallback
                    video_id = info.get('id')
                    for f in os.listdir(DOWNLOAD_DIR):
                        if video_id in f and os.path.getsize(os.path.join(DOWNLOAD_DIR, f)) > 0:
                            file_path = os.path.join(DOWNLOAD_DIR, f)
                            break
                    else:
                        raise Exception("yt-dlp reported success but no file found")

                if not file_path.endswith('.mp3'):
                    base_path = os.path.splitext(file_path)[0]
                    mp3_path = f"{base_path}.mp3"
                    if os.path.exists(file_path):
                        import subprocess
                        # PRO AUDIO CONVERTER: High-compatibility flags for Telegram VC
                        # -acodec libmp3lame: Standard MP3 encoder
                        # -ar 48000: Standard sample rate for Telegram VC
                        # -ac 2: Stereo audio (required for VC)
                        # -b:a 192k: Better bitrate for sound clarity
                        # -af "volume=2.0,loudnorm,dynaudnorm": Boost and normalize audio
                        # -map_metadata 0: Preserve metadata
                        subprocess.run([
                            'ffmpeg', '-y', '-i', file_path, 
                            '-vn', '-acodec', 'libmp3lame', 
                            '-b:a', '192k', '-ar', '48000', '-ac', '2', 
                            '-af', 'volume=2.0,loudnorm=I=-16:TP=-1.5:LRA=11,dynaudnorm=g=200',
                            '-map_metadata', '0',
                            mp3_path
                        ], check=True, capture_output=True)
                        
                        # Cleanup original if conversion succeeded
                        if os.path.exists(mp3_path) and os.path.getsize(mp3_path) > 1000:
                            try: os.remove(file_path)
                            except: pass
                            return mp3_path, info.get('title'), info.get('duration'), info.get('thumbnail')
                
                # Even if it is .mp3, let's re-encode it to ensure proper format/volume
                if file_path.endswith('.mp3'):
                    fixed_path = f"{file_path}_fixed.mp3"
                    import subprocess
                    try:
                        # Re-encode with Telegram VC optimized settings
                        subprocess.run([
                            'ffmpeg', '-y', '-i', file_path, 
                            '-acodec', 'libmp3lame', 
                            '-b:a', '192k', '-ar', '48000', '-ac', '2', 
                            '-af', 'volume=2.0,loudnorm=I=-16:TP=-1.5:LRA=11,dynaudnorm=g=200',
                            fixed_path
                        ], check=True, capture_output=True)
                        if os.path.exists(fixed_path) and os.path.getsize(fixed_path) > 10000:
                            os.replace(fixed_path, file_path)
                    except Exception as conv_err:
                        print(f"⚠️ MP3 post-processing failed: {conv_err}")
                        if os.path.exists(fixed_path): os.remove(fixed_path)
                
                return file_path, info.get('title'), info.get('duration'), info.get('thumbnail')
        return await loop.run_in_executor(None, _download)
    except Exception as e:
        LOGGER.error(f"❌ Download failed: {e}")
        return None, None, None, None

async def get_direct_stream_link(link: str, quality: str = "best", codec: str = "h264"):
    """Get direct stream URL without downloading"""
    LOGGER.info(f"🔗 Getting direct stream link for {link}")
    try:
        loop = asyncio.get_event_loop()
        def _extract_stream():
            opts = get_ydl_opts(codec_preference=codec)
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(link, download=False)
                return info.get('url'), info.get('title'), info.get('duration'), info.get('thumbnail')
        return await loop.run_in_executor(None, _extract_stream)
    except Exception as e:
        LOGGER.error(f"❌ Failed to get stream link: {e}")
        return None

async def download_song_simple(link: str) -> str:
    """Simple audio extraction logic inspired by wil92/youtube-audio-telegram-bot"""
    LOGGER.info(f"📥 Using simple extraction for: {link}")
    DOWNLOAD_DIR = "downloads"
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    
    # Generate a unique filename
    video_id = link.split('v=')[-1].split('&')[0] if 'v=' in link else str(random.randint(1000, 9999))
    file_path = os.path.join(DOWNLOAD_DIR, f"simple_{video_id}")
    
    # List of common User-Agents to rotate
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    
    try:
        ytdlp_path = "/root/GodVCMusicBot/venv/bin/yt-dlp" if os.path.exists("/root/GodVCMusicBot/venv/bin/yt-dlp") else "yt-dlp"
        
        # Optimized flags for high-quality, stable audio
        # Based on latest yt-dlp recommendations for Telegram bot integration
        cmd = [
            ytdlp_path,
            "-f", "ba[ext=m4a]/ba/b",
            "--audio-format", "mp3",
            "--audio-quality", "0",
            "-x",
            "--no-playlist",
            "--no-warnings",
            "--ignore-errors",
            "--geo-bypass",
            "--add-header", "Origin:https://www.youtube.com",
            "--add-header", "Referer:https://www.youtube.com/",
            "--user-agent", random.choice(USER_AGENTS),
            "--extractor-args", "youtube:player_client=android,ios,mweb,tv",
            "-o", f"{file_path}.%(ext)s",
            link
        ]
        
        # Add cookies if available
        cookie_path = "/root/GodVCMusicBot/cookies (3).txt"
        if os.path.exists(cookie_path):
            cmd.extend(["--cookies", cookie_path])
        elif os.path.exists("cookies (3).txt"):
            cmd.extend(["--cookies", "cookies (3).txt"])
            
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            final_path = f"{file_path}.mp3"
            # PRO AUDIO CONVERTER: Re-encode simple extraction to fix potential silent streams
            fixed_path = f"{file_path}_fixed.mp3"
            try:
                import subprocess
                # More robust conversion to fix potential silent streams
                # Using Telegram VC optimized settings:
                # -b:a 192k: Better clarity than 128k
                # -ar 48000: Perfect for Telegram VC
                # -ac 2: Stereo required for proper playback
                # -af volume=2.0,loudnorm,dynaudnorm: Maximum volume boost and normalization
                subprocess.run([
                    'ffmpeg', '-y', '-i', final_path, 
                    '-vn', # Disable video if present
                    '-acodec', 'libmp3lame', 
                    '-b:a', '192k', # Better bitrate for sound clarity
                    '-ar', '48000', # Standard sample rate for VC
                    '-ac', '2', 
                    '-af', 'volume=2.0,loudnorm=I=-16:TP=-1.5:LRA=11,dynaudnorm=g=200', # Boost and normalize
                    fixed_path
                ], check=True, capture_output=True)
                if os.path.exists(fixed_path) and os.path.getsize(fixed_path) > 10000:
                    os.replace(fixed_path, final_path)
            except Exception as conv_err:
                LOGGER.error(f"⚠️ Audio post-conversion failed: {conv_err}")
                if os.path.exists(fixed_path): os.remove(fixed_path)

            # Verify the file is not empty and is a valid audio file
            if os.path.exists(final_path) and os.path.getsize(final_path) > 10000: # At least 10KB
                LOGGER.info(f"✅ Simple extraction successful: {final_path}")
                return final_path
            else:
                LOGGER.error(f"❌ Simple extraction produced invalid file: {final_path}")
                if os.path.exists(final_path): os.remove(final_path)
        else:
            LOGGER.error(f"❌ Simple extraction failed: {stderr.decode()}")
    except Exception as e:
        LOGGER.error(f"❌ Simple extraction error: {e}")
    return None

async def download_song(link: str, quality: str = "best", codec: str = "h264") -> str:
    """Download audio from YouTube with reordered priorities for reliability"""
    global YOUR_API_URL
    if not YOUR_API_URL:
        await load_api_url()
        if not YOUR_API_URL:
            YOUR_API_URL = FALLBACK_API_URL
    
    video_id = link.split('v=')[-1].split('&')[0] if 'v=' in link else link
    DOWNLOAD_DIR = "downloads"
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id.split('/')[-1]}.mp3")
    
    # Check if file exists and is not empty
    if os.path.exists(file_path) and os.path.getsize(file_path) > 1000:
        return file_path
    elif os.path.exists(file_path):
        os.remove(file_path)

    # 1. Try simple extraction fallback first (PRIORITY 1: Proven most reliable recently)
    try:
        result = await download_song_simple(link)
        if result:
            return result
    except Exception as e:
        LOGGER.error(f"❌ download_song_simple failed: {e}")

    # 2. Try download_with_format_selection (PRIORITY 2: Advanced fallback)
    try:
        result = await download_with_format_selection(link, "best", "h264")
        if result and isinstance(result, tuple) and len(result) > 0 and result[0]:
            return result[0]
    except Exception as e:
        LOGGER.error(f"❌ download_with_format_selection failed: {e}")
    
    # 3. Try Shruti API (PRIORITY 3: External API fallback)
    try:
        async with aiohttp.ClientSession() as session:
            params = {"url": video_id, "type": "audio"}
            async with session.get(f"{YOUR_API_URL}/download", params=params, timeout=60) as response:
                if response.status == 200:
                    data = await response.json()
                    download_token = data.get("download_token")
                    if download_token:
                        stream_url = f"{YOUR_API_URL}/stream/{video_id}?type=audio"
                        async with session.get(stream_url, headers={"X-Download-Token": download_token}, timeout=300) as file_response:
                            if file_response.status == 200:
                                with open(file_path, "wb") as f:
                                    async for chunk in file_response.content.iter_chunked(16384):
                                        f.write(chunk)
                                return file_path
    except Exception as e:
        LOGGER.error(f"❌ Shruti API download failed: {e}")
        
    return None

async def download_video(link: str) -> str:
    """Download video with fallbacks including shell yt-dlp"""
    global YOUR_API_URL
    if not YOUR_API_URL:
        await load_api_url()
        if not YOUR_API_URL:
            YOUR_API_URL = FALLBACK_API_URL
    
    video_id = link.split('v=')[-1].split('&')[0] if 'v=' in link else link
    if '/' in video_id:
        video_id = video_id.split('/')[-1]
        
    DOWNLOAD_DIR = "downloads"
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp4")
    
    # Check if file exists and is valid
    if os.path.exists(file_path) and os.path.getsize(file_path) > 10000:
        return file_path
    elif os.path.exists(file_path):
        try: os.remove(file_path)
        except: pass

    # 1. Try Shell yt-dlp (Most robust for YouTube)
    try:
        LOGGER.info(f"📹 Trying shell yt-dlp for video: {link}")
        ytdlp_path = "/root/GodVCMusicBot/venv/bin/yt-dlp" if os.path.exists("/root/GodVCMusicBot/venv/bin/yt-dlp") else "yt-dlp"
        
        # Format for video: bestvideo+bestaudio or just best
        cmd = [
            ytdlp_path,
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "--merge-output-format", "mp4",
            "-o", file_path,
            "--no-warnings",
            "--ignore-errors",
            "--no-check-formats",
            "--geo-bypass",
            "--extractor-args", "youtube:player_client=android,ios,mweb,tv",
            link
        ]
        
        cookie_path = "/root/GodVCMusicBot/cookies (3).txt"
        if os.path.exists(cookie_path):
            cmd.extend(["--cookies", cookie_path])
            
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()
        
        if os.path.exists(file_path) and os.path.getsize(file_path) > 10000:
            LOGGER.info(f"✅ Video downloaded via shell: {file_path}")
            return file_path
    except Exception as e:
        LOGGER.error(f"❌ Video shell download failed: {e}")

    # 2. Try Shruti API (External fallback)
    try:
        LOGGER.info(f"📹 Trying Shruti API for video: {link}")
        async with aiohttp.ClientSession() as session:
            params = {"url": video_id, "type": "video"}
            async with session.get(f"{YOUR_API_URL}/download", params=params, timeout=60) as response:
                if response.status == 200:
                    data = await response.json()
                    download_token = data.get("download_token")
                    if download_token:
                        stream_url = f"{YOUR_API_URL}/stream/{video_id}?type=video"
                        async with session.get(stream_url, headers={"X-Download-Token": download_token}, timeout=600) as file_response:
                            if file_response.status == 200:
                                with open(file_path, "wb") as f:
                                    async for chunk in file_response.content.iter_chunked(16384):
                                        f.write(chunk)
                                if os.path.exists(file_path) and os.path.getsize(file_path) > 10000:
                                    LOGGER.info(f"✅ Video downloaded via Shruti API: {file_path}")
                                    return file_path
    except Exception as e:
        LOGGER.error(f"❌ Shruti API video download failed: {e}")

    return None

async def shell_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    out, errorz = await proc.communicate()
    return out.decode("utf-8")

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        return bool(re.search(self.regex, link))

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message: messages.append(message_1.reply_to_message)
        for message in messages:
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        return text[entity.offset: entity.offset + entity.length]
        return None

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        if "&" in link: link = link.split("&")[0]
        try:
            loop = asyncio.get_event_loop()
            def _extract_details():
                with yt_dlp.YoutubeDL(get_ydl_opts()) as ydl:
                    return ydl.extract_info(link, download=False)
            res = await loop.run_in_executor(None, _extract_details)
            return res["title"], str(res.get("duration")), res.get("duration", 0), res.get("thumbnail"), res["id"]
        except Exception:
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
        if videoid: link = self.base + link
        if "&" in link: link = link.split("&")[0]
        try:
            downloaded_file = await download_video(link)
            return (1, downloaded_file) if downloaded_file else (0, "Video download failed")
        except Exception as e:
            return 0, f"Video download error: {e}"

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid: link = self.listbase + link
        if "&" in link: link = link.split("&")[0]
        playlist = await shell_cmd(f"yt-dlp -i --get-id --flat-playlist --playlist-end {limit} --skip-download {link}")
        return [key for key in playlist.split("\n") if key]

    async def track(self, link: str, videoid: Union[bool, str] = None):
        title, duration_min, duration_sec, thumbnail, vidid = await self.details(link, videoid)
        return {"title": title, "link": f"https://www.youtube.com/watch?v={vidid}", "vidid": vidid, "duration_min": duration_min, "thumb": thumbnail}, vidid

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        if "&" in link: link = link.split("&")[0]
        loop = asyncio.get_event_loop()
        def _extract():
            with yt_dlp.YoutubeDL(get_ydl_opts()) as ydl:
                return ydl.extract_info(link, download=False)
        r = await loop.run_in_executor(None, _extract)
        formats_available = []
        for format in r["formats"]:
            if "dash" not in str(format["format"]).lower():
                formats_available.append({"format": format["format"], "filesize": format.get("filesize"), "format_id": format["format_id"], "ext": format["ext"], "format_note": format["format_note"], "yturl": link})
        return formats_available, link

    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        if "&" in link: link = link.split("&")[0]
        loop = asyncio.get_event_loop()
        def _extract():
            with yt_dlp.YoutubeDL(get_ydl_opts()) as ydl:
                return ydl.extract_info(f"ytsearch10:{link}", download=False)
        res_data = await loop.run_in_executor(None, _extract)
        if not res_data.get("entries"): raise Exception("No results found")
        result = res_data["entries"]
        return result[query_type]["title"], str(result[query_type]["duration"]), result[query_type]["thumbnail"], result[query_type]["id"]

    async def download(self, link: str, mystic, video: Union[bool, str] = None, videoid: Union[bool, str] = None, songaudio: Union[bool, str] = None, songvideo: Union[bool, str] = None, format_id: Union[bool, str] = None, title: Union[bool, str] = None) -> str:
        if videoid: link = self.base + link
        try:
            downloaded_file = await download_video(link) if video else await download_song(link)
            return (downloaded_file, True) if downloaded_file else (None, False)
        except Exception:
            return None, False

async def resolve_stream(webpage_url, video=False):
    """Resolve stream URL with multiple fallbacks including Tor"""
    LOGGER.info(f"🔗 RESOLVING {'VIDEO' if video else 'STREAM'}: {webpage_url}")
    if any(k in webpage_url for k in [".googlevideo.com", ".m3u8", ".mp3", ".mp4", "shrutibots.site"]):
        return webpage_url
    
    # Try shell-based resolution first as it's proven more robust now
    try:
        ytdlp_path = "/root/GodVCMusicBot/venv/bin/yt-dlp" if os.path.exists("/root/GodVCMusicBot/venv/bin/yt-dlp") else "yt-dlp"
        
        # If video requested, get best video format URL
        format_flag = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" if video else "ba[ext=m4a]/ba/b"
        
        cmd = [
            ytdlp_path, "-g", 
            "-f", format_flag,
            "--no-check-formats", "--ignore-no-formats-error",
            "--extractor-args", "youtube:player_client=tv,creator,ios,android,mweb",
            webpage_url
        ]
        
        cookie_path = "/root/GodVCMusicBot/cookies (3).txt"
        if os.path.exists(cookie_path):
            cmd.extend(["--cookies", cookie_path])
        elif os.path.exists("cookies (3).txt"):
            cmd.extend(["--cookies", "cookies (3).txt"])
            
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode == 0:
            lines = stdout.decode().strip().split('\n')
            # For video+audio, yt-dlp -g returns two URLs
            if video and len(lines) >= 2:
                # We return the first one (usually video) or the combined one if only one exists
                stream_url = lines[0] 
            else:
                stream_url = lines[0]
                
            if stream_url:
                LOGGER.info(f"✅ {'Video' if video else 'Stream'} resolved via Shell: {stream_url[:50]}...")
                return stream_url
    except Exception as e:
        LOGGER.warning(f"  ❌ Shell resolution failed: {e}")

    # Fallback to python-based resolution
    try:
        loop = asyncio.get_event_loop()
        def _extract_direct():
            opts = get_ydl_opts()
            if video:
                opts['format'] = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(webpage_url, download=False)["url"]
        return await loop.run_in_executor(None, _extract_direct)
    except Exception:
        pass
    
    # Final fallback to Tor
    try:
        loop = asyncio.get_event_loop()
        def _extract_tor():
            opts = get_ydl_opts(proxy="socks5://127.0.0.1:9050")
            if video:
                opts['format'] = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(webpage_url, download=False)["url"]
        return await loop.run_in_executor(None, _extract_tor)
    except Exception:
        pass

    # EXTRA: Final PyTube resolution if all else fails
    try:
        LOGGER.info(f"  → Final attempt: PyTube resolution for {webpage_url}")
        from pytube import YouTube
        yt = YouTube(webpage_url)
        stream = yt.streams.filter(only_audio=True).first()
        if stream:
            LOGGER.info(f"✅ Resolved via PyTube: {stream.url[:50]}...")
            return stream.url
    except Exception as e:
        LOGGER.warning(f"  ❌ PyTube resolution failed: {e}")

    raise Exception("Failed to resolve stream after all attempts")

# --- RapidAPI Configuration (Optional fallback) ---
# Users can add RAPID_API_KEY to .env for Black Hole API support
RAPID_API_KEY = os.getenv("RAPID_API_KEY") 

def extract_youtube_id(url: str) -> Optional[str]:
    """Robust YouTube ID extraction inspired by ytdl-inline-bot"""
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, url)
    return match.group(1) if match else None

async def search_blackhole_api(url: str) -> Optional[Dict[str, Any]]:
    """Black Hole API strategy (RapidAPI) for multi-platform support"""
    if not RAPID_API_KEY:
        return None
    
    LOGGER.info(f"🌀 Trying Black Hole API for: {url}")
    api_url = "https://social-download-all-in-one.p.rapidapi.com/v1/social/autolink"
    headers = {
        "x-rapidapi-key": RAPID_API_KEY,
        "x-rapidapi-host": "social-download-all-in-one.p.rapidapi.com",
        "Content-Type": "application/json"
    }
    payload = {"url": url}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, json=payload, headers=headers, timeout=15) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    medias = data.get("medias", [])
                    if medias:
                        # Pick the best quality audio or video
                        best = medias[0]
                        return {
                            "title": data.get("title", "Black Hole Download"),
                            "url": best.get("url"),
                            "thumbnail": data.get("thumbnail"),
                            "duration": 0, # API might not provide duration easily
                            "webpage_url": url,
                            "vidid": extract_youtube_id(url)
                        }
    except Exception as e:
        LOGGER.error(f"❌ Black Hole API failed: {e}")
    return None

async def search_youtube(query):
    """Search YouTube using multiple strategies reordered by recent effectiveness"""
    LOGGER.info(f"🔍 SEARCHING: {query}")
    
    # If query is a URL, try RapidAPI first as it's a powerful bypass
    if query.startswith(("http://", "https://")):
        res = await search_blackhole_api(query)
        if res: return res

    # 1. Try Shell-based yt-dlp Search (PRIORITY 1: Proven most robust recently)
    try:
        LOGGER.info("  → Strategy 1: Shell yt-dlp Search")
        # Use full path to venv yt-dlp and correct --cookies flag
        ytdlp_path = "/root/GodVCMusicBot/venv/bin/yt-dlp" if os.path.exists("/root/GodVCMusicBot/venv/bin/yt-dlp") else "yt-dlp"
        
        cmd = [
            ytdlp_path, 
            "--get-id", "--get-title", "--get-duration", "--get-thumbnail", 
            "--no-check-formats", "--ignore-no-formats-error",
            "--extractor-args", "youtube:player_client=tv,creator,ios,android,mweb",
            f"ytsearch1:{query}"
        ]
        
        # Add cookies if available
        cookie_path = "/root/GodVCMusicBot/cookies (3).txt"
        if os.path.exists(cookie_path):
            cmd.extend(["--cookies", cookie_path])
        elif os.path.exists("cookies (3).txt"):
            cmd.extend(["--cookies", "cookies (3).txt"])
            
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            lines = [l.strip() for l in stdout.decode().strip().split('\n') if l.strip()]
            if len(lines) >= 4:
                vidid = lines[0]
                title = lines[1]
                duration_str = lines[2]
                thumb = lines[3]
                
                final_duration = 0
                final_thumb = None
                
                for line in lines:
                    if ":" in line and not line.startswith("http"):
                        final_duration = time_to_seconds(line)
                    elif line.startswith("http"):
                        final_thumb = line
                
                LOGGER.info(f"✅ Found via Strategy 1 (Shell): {title}")
                return {
                    "title": title,
                    "url": None,
                    "thumbnail": final_thumb or thumb,
                    "webpage_url": f"https://www.youtube.com/watch?v={vidid}",
                    "duration": final_duration or 0,
                    "vidid": vidid
                }
    except Exception as e:
        LOGGER.error(f"  ❌ Strategy 1 failed: {e}")

    # 2. Try Fallen API (PRIORITY 2: Very reliable backup)
    res = await search_fallen_api(query)
    if res: return res

    # 3. Tor Fallback for Search (PRIORITY 3: High success rate when IP is throttled)
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

    # 4. Try Invidious Fallback
    res = await search_invidious(query)
    if res: return res

    # 5. Try direct yt-dlp search with cookies
    try:
        LOGGER.info("  → Strategy 5: Direct Search with Cookies")
        loop = asyncio.get_event_loop()
        def _extract_direct():
            search_opts = get_ydl_opts()
            with yt_dlp.YoutubeDL(search_opts) as ydl:
                return ydl.extract_info(f"ytsearch1:{query}", download=False)["entries"][0]
        
        res = await loop.run_in_executor(None, _extract_direct)
        if res:
            LOGGER.info(f"✅ Found via Strategy 5: {res.get('title')}")
            return {
                "title": res["title"], 
                "url": res.get("url"), 
                "thumbnail": res.get("thumbnail"), 
                "webpage_url": res.get("webpage_url"), 
                "duration": res.get("duration"), 
                "vidid": res.get("id")
            }
    except Exception as e:
        LOGGER.warning(f"  ❌ Strategy 5 failed: {e}")

    # 6. Try youtube-search-python (Local Search)
    try:
        LOGGER.info("  → Strategy 6: youtube-search-python")
        if VideosSearch:
            loop = asyncio.get_event_loop()
            def _sync_search():
                # Fix for TypeError: post() got an unexpected keyword argument 'proxies'
                # in some versions of youtube-search-python
                try:
                    search = VideosSearch(query, limit=1)
                    return search.result()
                except TypeError:
                    # Fallback if proxies argument is the issue
                    import httpx
                    # Monkeypatch httpx.post to ignore proxies if called from youtube-search-python
                    _old_post = httpx.post
                    def _new_post(*args, **kwargs):
                        if 'proxies' in kwargs:
                            del kwargs['proxies']
                        return _old_post(*args, **kwargs)
                    httpx.post = _new_post
                    try:
                        search = VideosSearch(query, limit=1)
                        res = search.result()
                        return res
                    finally:
                        httpx.post = _old_post
            
            result = await loop.run_in_executor(None, _sync_search)
            if result and result.get("result"):
                res = result["result"][0]
                LOGGER.info(f"✅ Found via Strategy 6: {res.get('title')}")
                return {
                    "title": res["title"],
                    "url": None, 
                    "thumbnail": res["thumbnails"][0]["url"] if res.get("thumbnails") else None,
                    "webpage_url": res["link"],
                    "duration": time_to_seconds(res.get("duration")),
                    "vidid": res.get("id")
                }
    except Exception as e:
        LOGGER.error(f"  ❌ Strategy 6 failed: {e}")

    # 7. Final attempt: PyTube search
    try:
        LOGGER.info("  → Strategy 7: PyTube Search")
        from pytube import Search
        s = Search(query)
        if s.results:
            res = s.results[0]
            LOGGER.info(f"✅ Found via Strategy 7: {res.title}")
            return {
                "title": res.title,
                "url": None,
                "thumbnail": res.thumbnail_url,
                "webpage_url": res.watch_url,
                "duration": res.length,
                "vidid": res.video_id
            }
    except Exception as e:
        LOGGER.error(f"  ❌ Strategy 7 failed: {e}")

    raise Exception("All search strategies failed. YouTube is blocking the server.")

async def search_youtube_video(query):
    return await search_youtube(query)
