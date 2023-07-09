import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
import jwt
import time
import json

# Spotify credentials
spotify_client_id = ''
spotify_client_secret = ''
spotify_redirect_uri = 'http://localhost:8000/'

# Apple Music credentials
apple_team_id = 'your_apple_team_id'
apple_key_id = 'your_apple_key_id'
apple_private_key = '''-----BEGIN PRIVATE KEY-----
Your Apple Private Key Here
-----END PRIVATE KEY-----'''

# Spotify setup
scope = 'user-library-read playlist-modify-public playlist-read-private'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=spotify_client_id,
                                               client_secret=spotify_client_secret,
                                               redirect_uri=spotify_redirect_uri,
                                               scope=scope))

# Get Spotify Playlist
spotify_playlist_id = 'your_spotify_playlist_id'
results = sp.playlist(spotify_playlist_id)
tracks = [track['track']['name'] + ' ' + track['track']['artists'][0]['name'] for track in results['tracks']['items']]

# Create Apple Music token
algorithm = 'ES256'
time_now = int(time.time())
time_expiration = time_now + 3600
headers = {
    'alg': algorithm,
    'kid': apple_key_id,
}
payload = {
    'iss': apple_team_id,
    'exp': time_expiration,
    'iat': time_now,
}
token = jwt.encode(payload, apple_private_key, algorithm=algorithm, headers=headers)

# Search tracks in Apple Music and get their ids
apple_track_ids = []
for track in tracks:
    response = requests.get('https://api.music.apple.com/v1/catalog/us/search', 
                            params={'term': track, 'limit': 1, 'types': 'songs'},
                            headers={'Authorization': 'Bearer ' + token})
    data = response.json()
    apple_track_ids.append(data['results']['songs']['data'][0]['id'])

# Create a playlist in Apple Music
playlist_payload = {
    "attributes": {
        "name": results['name'],
        "description": results['description']
    },
    "relationships": {
        "tracks": {
            "data": [{'id': track_id, 'type': 'songs'} for track_id in apple_track_ids]
        }
    }
}

response = requests.post('https://api.music.apple.com/v1/me/library/playlists', 
                         headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}, 
                         data=json.dumps(playlist_payload))
print(response.json())
