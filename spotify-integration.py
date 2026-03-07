import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import urllib.request
import json

# Spotify API credentials (get from https://developer.spotify.com/dashboard)
SPOTIFY_CLIENT_ID = "your_client_id_here"
SPOTIFY_CLIENT_SECRET = "your_client_secret_here"

def get_spotify_access_token():
    """Get Spotify access token"""
    try:
        auth_url = 'https://accounts.spotify.com/api/token'
        auth_response = urllib.request.urlopen(
            urllib.request.Request(
                auth_url,
                data=f'grant_type=client_credentials&client_id={SPOTIFY_CLIENT_ID}&client_secret={SPOTIFY_CLIENT_SECRET}'.encode(),
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                method='POST'
            )
        )
        auth_data = json.loads(auth_response.read())
        return auth_data.get('access_token')
    except Exception as e:
        print(f"❌ Spotify auth failed: {e}")
        return None

def search_spotify(query, limit=5):
    """Search Spotify and return track info"""
    try:
        access_token = get_spotify_access_token()
        if not access_token:
            return []
        
        # Search for tracks
        search_url = f'https://api.spotify.com/v1/search?q={urllib.parse.quote(query)}&type=track&limit={limit}'
        req = urllib.request.Request(
            search_url,
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read())
        
        tracks = []
        for item in data.get('tracks', {}).get('items', []):
            track_info = {
                'title': item['name'],
                'artist': item['artists'][0]['name'],
                'spotify_url': item['external_urls']['spotify'],
                'preview_url': item.get('preview_url'),  # 30-second preview
                'duration_ms': item['duration_ms'],
                'album': item['album']['name'],
                'album_art': item['album']['images'][0]['url'] if item['album']['images'] else None
            }
            tracks.append(track_info)
        
        return tracks
    
    except Exception as e:
        print(f"❌ Spotify search failed: {e}")
        return []

def search_youtube_for_spotify_track(track_info):
    """Convert Spotify track to YouTube search query"""
    query = f"{track_info['title']} {track_info['artist']}"
    return query

if __name__ == "__main__":
    # Test
    tracks = search_spotify("never gonna give you up")
    if tracks:
        print(f"Found {len(tracks)} tracks:")
        for track in tracks:
            print(f"  - {track['title']} by {track['artist']}")
