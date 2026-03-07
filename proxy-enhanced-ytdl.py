import yt_dlp
import os
import random
import urllib.request
import json

# Working Invidious instances (tested regularly)
INVIDIOUS_INSTANCES = [
    "https://invidious.io.lol",
    "https://invidious.fdn.fr", 
    "https://yewtu.be",
    "https://inv.riverside.rocks",
    "https://vid.puffyan.us",
    "https://invidious.privacydev.net",
]

def get_ydl_opts(clients=None, use_invidious=None, proxy=None):
    """Get yt-dlp options"""
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
        "socket_timeout": 30,
        "retries": 3
    }
    
    if proxy:
        opts["proxy"] = proxy
    
    if use_invidious:
        opts["invidious"] = use_invidious
    
    return opts

def fetch_proxies():
    """Fetch free proxies"""
    proxy_list = []
    try:
        # Try to fetch from multiple sources
        urls = [
            "https://api.proxyscrape.com/v2/?request=display&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        ]
        
        for url in urls:
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    proxies = response.read().decode().split('\n')
                    proxy_list.extend([p.strip() for p in proxies if ':' in p][:10])
            except:
                continue
        
        return proxy_list[:5]  # Return top 5
    except:
        return []

def search_youtube(query):
    """Search YouTube using proxies + Invidious"""
    
    print(f"\n🔍 Searching for: {query}")
    
    # Strategy 1: Try Invidious with proxies
    proxies = fetch_proxies()
    print(f"  📡 Fetched {len(proxies)} proxies")
    
    shuffled_instances = INVIDIOUS_INSTANCES.copy()
    random.shuffle(shuffled_instances)
    
    for instance in shuffled_instances:
        # Try without proxy first
        try:
            print(f"  → Testing Invidious: {instance}")
            opts = get_ydl_opts(use_indivious=instance, clients=["web"])
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                result = ydl.extract_info(f"ytsearch1:{query}", download=False)["entries"][0]
            
            print(f"  ✅ Success via Invidious!")
            
            direct_url = result.get("url")
            if "youtube.com" in direct_url or "youtu.be" in direct_url:
                print(f"  🔄 Extracting stream...")
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
            print(f"  ❌ Failed: {str(e)[:60]}")
            
            # Try with proxies
            for proxy in proxies[:2]:
                try:
                    print(f"     Trying proxy: {proxy[:40]}...")
                    opts = get_ydl_opts(use_invidious=instance, clients=["web"], proxy=f"http://{proxy}")
                    
                    with yt_dlp.YoutubeDL(opts) as ydl:
                        result = ydl.extract_info(f"ytsearch1:{query}", download=False)["entries"][0]
                    
                    print(f"  ✅ Success via Invidious + Proxy!")
                    
                    direct_url = result.get("url")
                    if "youtube.com" in direct_url or "youtu.be" in direct_url:
                        stream_info = ydl.extract_info(direct_url, download=False)
                        direct_url = stream_info.get("url")
                    
                    return {
                        "title": result.get("title"),
                        "url": direct_url,
                        "thumbnail": result.get("thumbnail"),
                        "webpage_url": result.get("webpage_url"),
                        "duration": result.get("duration"),
                    }
                except Exception as e2:
                    continue
    
    # Strategy 2: Try direct with different clients
    for client in ["tvclient", "ios", "android"]:
        try:
            print(f"  → Last resort: {client} client")
            opts = get_ydl_opts(clients=[client])
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                result = ydl.extract_info(f"ytsearch1:{query}", download=False)["entries"][0]
            
            print(f"  ✅ Success via direct ({client})!")
            
            direct_url = result.get("url")
            if "youtube.com" in direct_url or "youtu.be" in direct_url:
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
            print(f"  ❌ {client} failed: {str(e)[:60]}")
            continue
    
    raise Exception("All strategies failed - Server IP is blocked")

def search_youtube_video(query):
    return search_youtube(query)

def resolve_stream(webpage_url):
    """Resolve stream URL"""
    for client in ["android", "tvclient", "ios"]:
        try:
            opts = get_ydl_opts(clients=[client])
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(webpage_url, download=False)
                return info.get("url")
        except:
            continue
    
    raise Exception("Failed to resolve stream")
