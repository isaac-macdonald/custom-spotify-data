import os
from datetime import datetime, timedelta
import sqlite3

script_dir = os.path.dirname(os.path.abspath(__file__))

def get_minutes_in_timeframe(start_date, end_date):
    # Connect to the SQLite database
    conn = sqlite3.connect(os.path.join(script_dir, 'spotify_minutes.db'))
    cursor = conn.cursor()

    start_timestamp = int(start_date.timestamp() * 1000)
    end_timestamp = int(end_date.timestamp() * 1000)

    # Query to select all rows from the weekly_minutes table
    cursor.execute('SELECT SUM(duration_ms) FROM listened_songs WHERE played_at >= ? AND played_at <= ?', (start_timestamp, end_timestamp))

    milliseconds = cursor.fetchone()[0]
    conn.close()
    return milliseconds / 60000 if milliseconds else 0

def get_top_songs_in_timeframe(start_date, end_date):
    # Connect to the SQLite database
    conn = sqlite3.connect(os.path.join(script_dir, 'spotify_minutes.db'))
    cursor = conn.cursor()

    start_timestamp = int(start_date.timestamp() * 1000)
    end_timestamp = int(end_date.timestamp() * 1000)

    # Query to select all rows from the weekly_minutes table
    cursor.execute('''
        SELECT 
            song_id,
            name,
            album,
            artist,
            spotify_url,
            album_cover,
            COUNT(*) AS play_count,
            MAX(played_at) AS last_played
        FROM 
            listened_songs
        WHERE 
            played_at >= ?
        AND
            played_at <= ?
        GROUP BY 
            song_id
        ORDER BY 
            play_count DESC,
            last_played DESC
        LIMIT 10;

    ''', (start_timestamp, end_timestamp))

    songs = cursor.fetchall()
    conn.close()
    return songs if songs else None

def get_top_artists_in_timeframe(start_date, end_date):
    conn = sqlite3.connect(os.path.join(script_dir, 'spotify_minutes.db'))
    cursor = conn.cursor()

    start_timestamp = int(start_date.timestamp() * 1000)
    end_timestamp = int(end_date.timestamp() * 1000)

    # Query to select all rows from the weekly_minutes table
    cursor.execute('''
            SELECT 
                song_id,
                name,
                album,
                artist,
                spotify_url,
                album_cover,
                COUNT(*) AS artist_count,
                MAX(played_at) AS last_played
            FROM 
                listened_songs
            WHERE 
                played_at >= ?
            AND
                played_at <= ?
            GROUP BY 
                artist
            ORDER BY 
                artist_count DESC,
                last_played DESC
            LIMIT 10;

        ''', (start_timestamp, end_timestamp))

    songs = cursor.fetchall()
    conn.close()
    return songs if songs else None

def get_top_albums_in_timeframe(start_date, end_date):
    conn = sqlite3.connect(os.path.join(script_dir, 'spotify_minutes.db'))
    cursor = conn.cursor()

    start_timestamp = int(start_date.timestamp() * 1000)
    end_timestamp = int(end_date.timestamp() * 1000)

    # Query to select all rows from the weekly_minutes table
    cursor.execute('''
            SELECT 
                song_id,
                name,
                album,
                artist,
                spotify_url,
                album_cover,
                COUNT(*) AS album_count,
                MAX(played_at) AS last_played
            FROM 
                listened_songs
            WHERE 
                played_at >= ?
            AND
                played_at <= ?
            GROUP BY 
                album
            ORDER BY 
                album_count DESC,
                last_played DESC
            LIMIT 10;

        ''', (start_timestamp, end_timestamp))

    songs = cursor.fetchall()
    conn.close()
    return songs if songs else None

def get_songs_in_timeframe(start_date, end_date):
    conn = sqlite3.connect(os.path.join(script_dir, 'spotify_minutes.db'))
    cursor = conn.cursor()

    start_timestamp = int(start_date.timestamp() * 1000)
    end_timestamp = int(end_date.timestamp() * 1000)

    # Query to select all rows from the weekly_minutes table
    cursor.execute('''
            SELECT 
                *
            FROM 
                listened_songs
            WHERE 
                played_at >= ?
            AND
                played_at <= ?;
        ''', (start_timestamp, end_timestamp))

    songs = cursor.fetchall()
    conn.close()
    return songs if songs else None

def get_weekly_minutes():
    current_date = datetime.today()
    one_week_ago = current_date - timedelta(days=7)
    return get_minutes_in_timeframe(one_week_ago, current_date)

def get_weekly_top_songs():
    current_date = datetime.today()
    one_week_ago = current_date - timedelta(days=7)
    return get_top_songs_in_timeframe(one_week_ago, current_date)

def get_weekly_top_artists():
    current_date = datetime.today()
    one_week_ago = current_date - timedelta(days=7)
    return get_top_artists_in_timeframe(one_week_ago, current_date)

def get_weekly_top_albums():
    current_date = datetime.today()
    one_week_ago = current_date - timedelta(days=7)
    return get_top_artists_in_timeframe(one_week_ago, current_date)

def get_weekly_songs():
    current_date = datetime.today()
    one_week_ago = current_date - timedelta(days=7)
    return get_songs_in_timeframe(one_week_ago, current_date)

def get_all_time_minutes():
    current_date = datetime.today()
    one_week_ago = current_date - timedelta(weeks=200)
    return get_minutes_in_timeframe(one_week_ago, current_date)

def get_all_time_top_songs():
    current_date = datetime.today()
    one_week_ago = current_date - timedelta(weeks=200)
    return get_top_songs_in_timeframe(one_week_ago, current_date)

def get_all_time_artists():
    current_date = datetime.today()
    one_week_ago = current_date - timedelta(weeks=200)
    return get_top_artists_in_timeframe(one_week_ago, current_date)

def get_all_time_albums():
    current_date = datetime.today()
    one_week_ago = current_date - timedelta(weeks=200)
    return get_top_artists_in_timeframe(one_week_ago, current_date)

def get_all_time_songs():
    current_date = datetime.today()
    one_week_ago = current_date - timedelta(weeks=200)
    return get_songs_in_timeframe(one_week_ago, current_date)

def get_last_week_dates():
    # Get the current date
    current_date = datetime.today()

    # Find the most recent Monday (start of the current week)
    days_since_monday = current_date.weekday()  # Monday is 0
    most_recent_monday = current_date - timedelta(days=days_since_monday)

    # The start of the previous week is 7 days before the most recent Monday
    start_of_last_week = most_recent_monday - timedelta(days=7)

    # The end of the previous week is the most recent Monday (start of the current week)
    end_of_last_week = most_recent_monday

    # Set both to 12:00 AM (midnight) by replacing hour, minute, second, microsecond
    start_of_last_week = start_of_last_week.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_last_week = end_of_last_week.replace(hour=0, minute=0, second=0, microsecond=0)

    return start_of_last_week, end_of_last_week

def get_last_week_minutes():
    start_of_last_week, end_of_last_week = get_last_week_dates()
    return get_minutes_in_timeframe(start_of_last_week, end_of_last_week)

def get_last_week_top_songs():
    start_of_last_week, end_of_last_week = get_last_week_dates()
    return get_top_songs_in_timeframe(start_of_last_week, end_of_last_week)

def get_last_week_top_artists():
    start_of_last_week, end_of_last_week = get_last_week_dates()
    return get_top_artists_in_timeframe(start_of_last_week, end_of_last_week)

def get_last_week_top_albums():
    start_of_last_week, end_of_last_week = get_last_week_dates()
    return get_top_albums_in_timeframe(start_of_last_week, end_of_last_week)

def get_last_week_songs():
    start_of_last_week, end_of_last_week = get_last_week_dates()
    return get_songs_in_timeframe(start_of_last_week, end_of_last_week)

def has_email_been_sent():
    current_date = datetime.today()

    # Calculate the most recent Monday (start of this week)
    days_since_monday = current_date.weekday()  # Monday is 0
    monday_of_this_week = current_date - timedelta(days=days_since_monday)

    # Set time to 12:00 AM (midnight)
    monday_of_this_week = monday_of_this_week.replace(hour=0, minute=0, second=0, microsecond=0)

    conn = sqlite3.connect(os.path.join(script_dir, 'spotify_minutes.db'))
    cursor = conn.cursor()

    # Insert the date of Monday into the sent_emails table
    cursor.execute('''
                SELECT sent
                FROM sent_emails
                ORDER BY sent DESC;
            ''')
    result = cursor.fetchall()
    if result is None or len(result) == 0:
        return False
    # Commit the transaction and close the connection
    print(cursor.fetchall())
    last_date = result[0]
    conn.commit()
    conn.close()
    print(f"Monday {monday_of_this_week}")
    print(f"Retrieved {last_date}")
    return str(monday_of_this_week) in str(last_date)


def set_email_sent_for_week():
    current_date = datetime.today()

    # Calculate the most recent Monday (start of this week)
    days_since_monday = current_date.weekday()  # Monday is 0
    monday_of_this_week = current_date - timedelta(days=days_since_monday)

    # Set time to 12:00 AM (midnight)
    monday_of_this_week = monday_of_this_week.replace(hour=0, minute=0, second=0, microsecond=0)
    conn = sqlite3.connect(os.path.join(script_dir, 'spotify_minutes.db'))
    cursor = conn.cursor()

    # Insert the date of Monday into the sent_emails table
    cursor.execute('''
            INSERT OR REPLACE INTO sent_emails (sent) 
            VALUES (?);
        ''', (monday_of_this_week, ))

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()

print(get_weekly_top_artists())






