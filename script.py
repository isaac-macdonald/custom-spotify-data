import sqlite3
import time
from datetime import datetime, timedelta
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
from queries import get_weekly_songs, get_autumn_songs
import logging
import os

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import base64

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
SCOPE = "user-top-read user-read-recently-played playlist-modify-public ugc-image-upload"
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
from base64 import b64decode

def replace_playlist_with_tracks(track_rows, playlist_name, season="Autumn", year=2024):
    try:
        user_id = sp.me()['id']

        # Extract song IDs from tuples
        track_ids = [row[0] for row in track_rows]

        # Check for existing playlist
        playlists = sp.current_user_playlists()
        existing_playlist = next(
            (p for p in playlists['items'] if p['name'].lower() == playlist_name.lower()),
            None
        )

        if existing_playlist:
            logging.info(f"Deleting existing playlist '{playlist_name}'")
            sp.current_user_unfollow_playlist(existing_playlist['id'])
            time.sleep(1)  # Avoid race condition

        logging.info(f"Creating new playlist '{playlist_name}'")
        new_playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=True, description=f"This playlist is autogenerated and is my top 100 songs listened to this season.    Last updated: {datetime.now().strftime('%d-%m-%Y %H:%M')}")
        playlist_id = new_playlist['id']

        # Convert to Spotify URIs
        track_uris = [f"spotify:track:{track_id}" for track_id in track_ids]

        # Add in chunks of 100
        for i in range(0, len(track_uris), 100):
            sp.playlist_add_items(playlist_id, track_uris[i:i + 100])

        logging.info(f"✅ Added {len(track_uris)} tracks to playlist '{playlist_name}'")

        # Generate and upload cover
        cover_base64 = generate_stylized_cover(season=season, year=year)

        sp.playlist_upload_cover_image(playlist_id, cover_base64)
        logging.info("📀 Uploaded custom playlist cover")

    except Exception as e:
        logging.error(f"Error replacing playlist: {e}")



def generate_stylized_cover(season="Autumn", year=2024):
    # Define seasonal styles
    styles = {
        "Autumn": {"bg": "#B24C00", "text": "#FFF8E7"},
        "Winter": {"bg": "#1C2C4C", "text": "#CDE8FF"},
        "Spring": {"bg": "#A8D5BA", "text": "#1D3B2A"},
        "Summer": {"bg": "#F9C74F", "text": "#F94144"},
    }

    style = styles.get(season.capitalize(), styles["Autumn"])
    text_color = style["text"]
    bg_color = style["bg"]

    size = (640, 640)
    font_size_main = 60
    font_size_sub = 30

    img = Image.new("RGB", size, color=bg_color)
    draw = ImageDraw.Draw(img)

    try:
        font_main = ImageFont.truetype("fonts/JetBrainsMono-BoldItalic.ttf", font_size_main)
        font_sub = ImageFont.truetype("fonts/JetBrainsMono-Regular.ttf", font_size_sub)
    except IOError:
        font_main = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    title_text = f"{season.upper()} {year}"
    subtitle_text = "Top Tracks"

    # Center main text using textbbox instead of deprecated textsize
    main_bbox = draw.textbbox((0, 0), title_text, font=font_main)
    main_width = main_bbox[2] - main_bbox[0]
    main_height = main_bbox[3] - main_bbox[1]
    main_position = ((size[0] - main_width) / 2, (size[1] - main_height) / 2 - 20)
    draw.text(main_position, title_text, fill=text_color, font=font_main)

    # Center subtext
    sub_bbox = draw.textbbox((0, 0), subtitle_text, font=font_sub)
    sub_width = sub_bbox[2] - sub_bbox[0]
    sub_position = ((size[0] - sub_width) / 2, main_position[1] + main_height + 20)
    draw.text(sub_position, subtitle_text, fill=text_color, font=font_sub)

    buffer = BytesIO()
    img.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")



# Run the function once when the script is executed
create_db()
get_minutes_played_since_last_run()
autumn_tracks = get_autumn_songs()
replace_playlist_with_tracks(autumn_tracks, 'top autumn tracks')


