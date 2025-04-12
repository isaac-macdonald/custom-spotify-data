import sqlite3
import time
from datetime import datetime, timedelta
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
from queries import get_weekly_songs
import logging
import os


# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Log file path in the same directory as the script
log_file = os.path.join(script_dir, "spotify_minutes.log")

# Set up logging: create the log file if it doesn't exist and append logs
logging.basicConfig(filename=log_file, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
load_dotenv()
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = "http://127.0.0.1:8090"
SCOPE = "user-top-read user-read-recently-played"
token_cache = "token_cache.json"  # A file to store tokens

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID,
                                               client_secret=SPOTIFY_CLIENT_SECRET,
                                               redirect_uri=SPOTIFY_REDIRECT_URI,
                                               scope=SCOPE,
                                               cache_path=token_cache))


def create_db():
    try:
        db_path = os.path.join(script_dir, 'spotify_minutes.db')  # Absolute path
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS listened_songs (
            song_id TEXT,
            name TEXT,
            album TEXT,
            artist TEXT,
            spotify_url TEXT,
            album_cover TEXT,
            played_at INTEGER PRIMARY KEY,
            duration_ms INTEGER
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sent_emails (
            sent DATETIME PRIMARY KEY
        )
        ''')

        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"Error creating database: {e}")

def insert_song(song_info):
    try:
        db_path = os.path.join(script_dir, 'spotify_minutes.db')  # Absolute path
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
        INSERT OR REPLACE INTO listened_songs (song_id, name, album, artist, spotify_url, album_cover, played_at, duration_ms)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', song_info)
        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"Error inserting song: {e}")

def get_last_played_timestamp():
    try:
        db_path = os.path.join(script_dir, 'spotify_minutes.db')  # Absolute path
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT MAX(played_at) FROM listened_songs')
        result = cursor.fetchone()
        if result and result[0] is not None:
            return result[0]
        else:
            return None
    except Exception as e:
        logging.error(f"Error fetching last played timestamp: {e}")
        return None



def get_track_features(id):
    meta = sp.track(id)
    name = meta['name']
    album = meta['album']['name']
    artist = meta['album']['artists'][0]['name']
    spotify_url = meta['external_urls']['spotify']
    album_cover = meta['album']['images'][0]['url']
    track_info = [name, album, artist, spotify_url, album_cover]
    return track_info

def get_minutes_played_since_last_run():
    try:
        last_run_timestamp = get_last_played_timestamp()
        if last_run_timestamp is None:
            # If this is the first run, set the timestamp to 0
            last_run_timestamp = 0

        # Fetch the most recent tracks played since the last run
        recent_tracks = sp.current_user_recently_played(limit=50)
        tracks_added = 0

        for track in recent_tracks['items']:
            played_at = track['played_at']
            played_at_timestamp = int(time.mktime(datetime.strptime(played_at, "%Y-%m-%dT%H:%M:%S.%fZ").timetuple()) * 1000)


            # Only add tracks played after the last run
            if played_at_timestamp > last_run_timestamp:
                logging.info("--  ADDING  --")
                                # Get track features and include played_at_timestamp
                track_info = get_track_features(track['track']['id'])
                song_info = [track['track']['id']] + track_info + [played_at_timestamp, track['track']['duration_ms']]
                logging.info(song_info)
                # Insert the song with the correct data
                insert_song(song_info)
                tracks_added += 1

        if tracks_added == 50:
            logging.warning("WARNING: 50 new tracks retrieved. Some tracks might have been missed due to API limitations.")
        elif tracks_added == 0:
            logging.info(f"Found no songs")

    except Exception as e:
        logging.error(f"Error in getting minutes played: {e}")

def get_artist_image_from_song_id(song_id):
    meta = sp.track(song_id)
    artist = sp.artist(meta['artists'][0]['id'])
    image = artist['images'][0]['url']
    return image

def get_top_genres(songs):
    """WIP - Not every artist has genres associated with it"""

# Run the function once when the script is executed
create_db()
get_minutes_played_since_last_run()
