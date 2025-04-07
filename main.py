import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import time
import datetime

SPOTIFY_CLIENT_ID = "cf6f3d0bc37a47afa5238cb72778ec47"
SPOTIFY_CLIENT_SECRET = "631edfd5d7d34486af26e5368609fce5"
SPOTIFY_REDIRECT_URI = "http://127.0.0.1:8090"
SCOPE = "user-top-read user-read-recently-played"

token_cache = "token_cache.json"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID,
                                               client_secret=SPOTIFY_CLIENT_SECRET,
                                               redirect_uri=SPOTIFY_REDIRECT_URI,
                                               scope=SCOPE,
                                               cache_path='token_cache.json'))

top_tracks_short = sp.current_user_top_tracks(limit=10, offset=0, time_range="short_term")
recent_tracks = sp.current_user_recently_played(limit=1)

def get_track_ids(time_frame):
    track_ids = []
    for song in time_frame['items']:
        track_ids.append(song['track']['id'])
    return track_ids

track_ids = get_track_ids(recent_tracks)

def get_track_features(id):
    meta = sp.track(id)
    name = meta['name']
    album = meta['album']['name']
    artist = meta['album']['artists'][0]['name']
    spotify_url = meta['external_urls']['spotify']
    album_cover = meta['album']['images'][0]['url']
    track_info = [name, album, artist, spotify_url, album_cover]
    return track_info

tracks = []

for i in range(len(track_ids)):
    time.sleep(0.5)
    track = get_track_features(track_ids[i])
    tracks.append(track)

df = pd.DataFrame(tracks, columns = ['name', 'album', 'artist', 'spotify_url', 'album_cover'])
print(df.head(5))