import yt_dlp
import os
import random
import urllib.request
import json
import subprocess

# List of Invidious instances
INVIDIOUS_INSTANCES = [
    "https://invidious.io.lol",
    "https://invidious.fdn.fr",
    "https://yewtu.be",
    "https://inv.riverside.rocks",
    "https://vid.puffyan.us",
    "https://invidious.privacydev.net",
]

def check_vpn_active():
    """Check if VPN is active and get VPN IP"""
    try:
        # Check if WireGuard interface exists
        result = subprocess.run(['ip', 'addr', 'show', 'wg0'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and 'state UP' in result.stdout:
            # Get VPN IP
            vpn_check = urllib.request.urlopen('http://ifconfig.me/ip', timeout=10).read().decode().strip()
            return True, vpn_check
        return False, None
    except:
        return False, None

def fetch_working_proxies():
    """Fetch free working proxies"""
    proxy_urls = [
        "https://api.proxyscrape.com/v2/?request=display&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
    ]
    
    proxies = []
    for url in proxy_urls:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = response.read().decode("utf-8", errors="ignore")
                found = [p.strip() for p in data.split("\n") if ":" in p and len(p.split(":")) == 2]
                proxies.extend(found[:5])
        except Exception as e:
            print(f"  ⚠️ Proxy list failed: {str(e)[:40]}")
            continue
    
    random.shuffle(proxies)
    return proxies[:10]

def get_ydl_opts(clients=None, use_invidious=None, proxy=None):
    """Get yt-dlp options with optional proxy"""
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
        "retries": 2
    }
    
    if proxy:
        opts["proxy"] = proxy
        print(f"     🌐 Using proxy: {proxy[:50]}...")
    
    if use_invidious:
        opts["invidious"] = use_invidious
        print(f"     🔄 Using Invidious: {use_invidious}")
    
    return opts

def search_youtube(query):
    """Search YouTube using VPN + Invidious + proxy fallback"""
    
    print(f"\n🔍 Searching for: {query}")
    
    # Check if VPN is active
    vpn_active, vpn_ip = check_vpn_active()
    if vpn_active:
        print(f"  ✅ VPN detected! IP: {vpn_ip}")
    
    # Fetch proxies
    proxies = fetch_working_proxies()
    print(f"  📡 Fetched {len(proxies)} proxies")
    
    # Strategy 1: Try Invidious instances (with and without proxies/VPN)
    shuffled_instances = INVIDIOUS_INSTANCES.copy()
    random.shuffle(shuffled_instances)
    
    for instance in shuffled_instances:
        # Try without proxy first
        try:
            print(f"  → Testing Invidious: {instance}")
            opts = get_ydl_opts(use_invidious=instance, clients=["web"])
            
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
            error_msg = str(e)
            print(f"  ❌ Failed: {error_msg[:60]}")
            
            # Try with 2-3 proxies
            for proxy in proxies[:3]:
                try:
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
    
    # Strategy 2: Direct YouTube with different clients + proxies
    for client in ["tvclient", "ios", "android"]:
        for proxy in proxies[:2]:
            try:
                print(f"  → Trying {client} client with proxy")
                opts = get_ydl_opts(clients=[client], proxy=f"http://{proxy}")
                
                with yt_dlp.YoutubeDL(opts) as ydl:
                    result = ydl.extract_info(f"ytsearch1:{query}", download=False)["entries"][0]
                
                print(f"  ✅ Success via direct ({client}) + Proxy!")
                
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
            except:
                continue
    
    raise Exception("All strategies failed - Server IP is blocked by YouTube")

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
