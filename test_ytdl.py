import yt_dlp
import os

def get_ydl_opts(clients=None, use_invidious=None):
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
    
    if use_invidious:
        opts["invidious"] = use_invidious
    
    return opts

# Test different approaches
query = "test"

print("=" * 60)
print("TESTING YOUTUBE SEARCH STRATEGIES")
print("=" * 60)

# Test 1: Direct with Android client + cookies
print("\n1. Testing Android client with cookies...")
try:
    cookie_path = "/root/GodVCMusicBot/GodVCMusicBot/youtube_cookies.txt"
    opts = get_ydl_opts(clients=["android"])
    if os.path.exists(cookie_path):
        opts["cookiefile"] = cookie_path
        print("   🍪 Using cookies")
    
    with yt_dlp.YoutubeDL(opts) as ydl:
        result = ydl.extract_info(f"ytsearch1:{query}", download=False)["entries"][0]
    
    print(f"   ✅ SUCCESS! Title: {result.get('title')}")
    print(f"   URL type: {'Direct' if 'googlevideo.com' in result.get('url', '') else 'Webpage'}")
except Exception as e:
    print(f"   ❌ FAILED: {str(e)[:80]}")

# Test 2: iOS client
print("\n2. Testing iOS client...")
try:
    opts = get_ydl_opts(clients=["ios"])
    with yt_dlp.YoutubeDL(opts) as ydl:
        result = ydl.extract_info(f"ytsearch1:{query}", download=False)["entries"][0]
    
    print(f"   ✅ SUCCESS! Title: {result.get('title')}")
except Exception as e:
    print(f"   ❌ FAILED: {str(e)[:80]}")

# Test 3: TV client
print("\n3. Testing TV client...")
try:
    opts = get_ydl_opts(clients=["tvclient"])
    with yt_dlp.YoutubeDL(opts) as ydl:
        result = ydl.extract_info(f"ytsearch1:{query}", download=False)["entries"][0]
    
    print(f"   ✅ SUCCESS! Title: {result.get('title')}")
except Exception as e:
    print(f"   ❌ FAILED: {str(e)[:80]}")

# Test 4: Invidious instances
print("\n4. Testing Invidious instances...")
instances = [
    "https://invidious.io.lol",
    "https://invidious.fdn.fr",
    "https://yewtu.be",
    "https://inv.riverside.rocks",
    "https://invidious.blamefran.net",
]

for instance in instances:
    try:
        print(f"   → Testing {instance}...")
        opts = get_ydl_opts(clients=["web"], use_invidious=instance)
        with yt_dlp.YoutubeDL(opts) as ydl:
            result = ydl.extract_info(f"ytsearch1:{query}", download=False)["entries"][0]
        
        print(f"      ✅ {instance[:40]} WORKS!")
    except Exception as e:
        print(f"      ❌ {instance[:40]} FAILED")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
