import yt_dlp
import os
import random
import requests
from bs4 import BeautifulSoup

# List of Invidious instances (alternative YouTube frontends)
INVIDIOUS_INSTANCES = [
    "https://invidious.io.lol",
    "https://invidious.fdn.fr",
    "https://yewtu.be",
    "https://inv.riverside.rocks",
    "https://invidious.blamefran.net",
]

def get_ydl_opts(proxy=None):
    """Get yt-dlp options with optional proxy support"""
    
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
        "socket_timeout": 15,  # Shorter timeout for dead proxies
        "retries": 2  # Fewer retries for speed
    }
    
    # Add proxy if provided
    if proxy:
        opts["proxy"] = proxy
        print(f"  🌐 Using proxy: {proxy}")
    
    return opts

def fetch_fresh_proxies():
    """Fetch fresh proxies from free sources"""
    proxy_list = []
    
    try:
        # Try ProxyNova
        response = requests.get("https://www.proxynova.com/proxy-server-list/", timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        for row in soup.select('tr'):
            cells = row.select('td')
            if len(cells) >= 2:
                ip = cells[0].get('data-ip') or cells[0].text.strip()
                port = cells[1].text.strip()
                if ip and port and port.isdigit():
                    proxy_list.append(f"http://{ip}:{port}")
    except Exception as e:
        print(f"  ⚠️ Failed to fetch proxies: {str(e)[:50]}")
    
    # Fallback hardcoded list (these change frequently)
    if not proxy_list:
        proxy_list = [
            "http://185.199.229.156:7494",
            "http://185.199.230.156:7495",
            "http://47.88.62.41:8080",
            "http://103.155.217.156:41367",
            "http://103.152.112.120:80",
            "http://185.217.136.28:1337",
            "http://20.206.106.216:8123",
            "http://103.167.135.110:80",
        ]
    
    return proxy_list

def search_youtube(query):
    """Search YouTube using multiple strategies including fresh proxies"""
    
    print(f"🔍 Searching: {query}")
    
    # Strategy 1: Try direct connection first
    try:
        print(f"  → Attempt 1: Direct connection")
        opts = get_ydl_opts()
        
        with yt_dlp.YoutubeDL(opts) as ydl:
            result = ydl.extract_info(f"ytsearch:{query}", download=False)["entries"][0]
        
        print(f"  ✅ Success via direct!")
        return {
            "title": result.get("title"),
            "url": result.get("url"),
            "thumbnail": result.get("thumbnail"),
            "webpage_url": result.get("webpage_url"),
            "duration": result.get("duration"),
        }
    except Exception as e:
        print(f"  ❌ Direct failed: {str(e)[:80]}")
    
    # Strategy 2: Fetch and try fresh proxies
    try:
        print(f"  🔄 Fetching fresh proxies...")
        proxy_list = fetch_fresh_proxies()
        print(f"  📦 Got {len(proxy_list)} proxies, trying top 5...")
        
        for i, proxy in enumerate(proxy_list[:5], start=2):
            try:
                print(f"  → Attempt {i}: {proxy}")
                opts = get_ydl_opts(proxy=proxy)
                
                with yt_dlp.YoutubeDL(opts) as ydl:
                    result = ydl.extract_info(f"ytsearch:{query}", download=False)["entries"][0]
                
                print(f"  ✅ Success via proxy!")
                return {
                    "title": result.get("title"),
                    "url": result.get("url"),
                    "thumbnail": result.get("thumbnail"),
                    "webpage_url": result.get("webpage_url"),
                    "duration": result.get("duration"),
                }
            except Exception as e:
                print(f"  ❌ Proxy failed: {str(e)[:50]}")
                continue
    except Exception as e:
        print(f"  ⚠️ Proxy strategy failed: {str(e)[:50]}")
    
    # Strategy 3: Try Invidious instances
    for instance in INVIDIOUS_INSTANCES:
        try:
            print(f"  → Trying Invidious: {instance}")
            opts = get_ydl_opts()
            opts["invidious"] = instance
            
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
            print(f"  ❌ Invidious failed: {str(e)[:50]}")
            continue
    
    raise Exception("All strategies failed")

def search_youtube_video(query):
    return search_youtube(query)

def resolve_stream(webpage_url):
    """Resolve stream URL with proxy support"""
    
    # Try direct first
    try:
        print(f"  → Resolving directly...")
        opts = get_ydl_opts()
        
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(webpage_url, download=False)
            return info.get("url")
    except Exception as e:
        print(f"  ❌ Direct failed: {str(e)[:50]}")
    
    # Try with fresh proxies
    try:
        proxy_list = fetch_fresh_proxies()
        for proxy in proxy_list[:3]:
            try:
                print(f"  → Trying proxy: {proxy}")
                opts = get_ydl_opts(proxy=proxy)
                
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(webpage_url, download=False)
                    return info.get("url")
            except Exception as e:
                print(f"  ❌ Proxy failed: {str(e)[:50]}")
                continue
    except Exception as e:
        print(f"  ⚠️ Proxy resolution failed: {str(e)[:50]}")
    
    raise Exception("Failed to resolve stream")
