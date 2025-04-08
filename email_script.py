import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
from script import get_artist_image_from_song_id
from queries import get_weekly_top_artists, get_weekly_top_songs, get_weekly_minutes, get_weekly_top_albums, \
    get_last_week_minutes, get_last_week_top_songs, get_last_week_top_artists, get_last_week_top_albums, \
    has_email_been_sent, set_email_sent_for_week, get_all_time_minutes, get_all_time_top_songs, get_all_time_artists, \
    get_all_time_albums
import os

load_dotenv()

script_dir = os.path.dirname(os.path.abspath(__file__))

def send_html_email(subject, body, to_email):
    if(has_email_been_sent()):
        print("email been sent")
        return
    else:
        set_email_sent_for_week()
    print("email not been sent")
    # Sender's email credentials
    from_email = "imacdonald135@gmail.com"
    from_password = os.getenv("EMAIL_APP_PASSWORD")  # Use an app-specific password if 2FA is enabled

    # Setup the MIME
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # Attach the HTML body with the msg instance
    msg.attach(MIMEText(body, 'html'))

    # Set up the SMTP server (using Gmail's SMTP server here)
    try:
        # Establish a connection to Gmail's SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Start TLS encryption
        server.login(from_email, from_password)  # Log in to the email server

        # Send the email
        server.sendmail(from_email, to_email, msg.as_string())

        # Close the server connection
        server.quit()

        print("Email sent successfully.")

    except Exception as e:
        print(f"Failed to send email. Error: {e}")

def generate_html_from_template(template_path, replacements):
    # Read the template HTML file
    with open(template_path, 'r') as file:
        html_content = file.read()

    # Replace placeholders with actual values
    for placeholder, value in replacements.items():
        html_content = html_content.replace(f"{{{{ {placeholder} }}}}", str(value))
    return html_content

weekly_minutes = get_last_week_minutes()
top_songs = get_last_week_top_songs()
top_artists = get_last_week_top_artists()
top_albums = get_last_week_top_albums()
at_minutes = get_all_time_minutes()
at_top_songs = get_all_time_top_songs()
at_top_artists = get_all_time_artists()
at_top_albums = get_all_time_albums()

# Replace these values with actual data
replacements = {
    "minutes": int(weekly_minutes),
    "song1": top_songs[0][1],
    "song2": top_songs[1][1],
    "song3": top_songs[2][1],
    "song4": top_songs[3][1],
    "song5": top_songs[4][1],
    "song1artist": top_songs[0][3],
    "song2artist": top_songs[1][3],
    "song3artist": top_songs[2][3],
    "song4artist": top_songs[3][3],
    "song5artist": top_songs[4][3],
    "song1count": top_songs[0][6],
    "song2count": top_songs[1][6],
    "song3count": top_songs[2][6],
    "song4count": top_songs[3][6],
    "song5count": top_songs[4][6],
    "artist1": top_artists[0][3],
    "artist2": top_artists[1][3],
    "artist3": top_artists[2][3],
    "artist4": top_artists[3][3],
    "artist5": top_artists[4][3],
    "artist1cover": get_artist_image_from_song_id(top_albums[0][0]),
    "artist2cover": get_artist_image_from_song_id(top_albums[1][0]),
    "artist3cover": get_artist_image_from_song_id(top_albums[2][0]),
    "artist4cover": get_artist_image_from_song_id(top_albums[3][0]),
    "artist5cover": get_artist_image_from_song_id(top_albums[4][0]),
    "album1": top_albums[0][2],
    "album2": top_albums[1][2],
    "album3": top_albums[2][2],
    "album4": top_albums[3][2],
    "album5": top_albums[4][2],
    "album1cover": top_albums[0][5],
    "album2cover": top_albums[1][5],
    "album3cover": top_albums[2][5],
    "album4cover": top_albums[3][5],
    "album5cover": top_albums[4][5],
    "at_minutes": int(at_minutes),
    "at_song1": at_top_songs[0][1],
    "at_song2": at_top_songs[1][1],
    "at_song3": at_top_songs[2][1],
    "at_song4": at_top_songs[3][1],
    "at_song5": at_top_songs[4][1],
    "at_song6": at_top_songs[5][1],
    "at_song7": at_top_songs[6][1],
    "at_song8": at_top_songs[7][1],
    "at_song9": at_top_songs[8][1],
    "at_song10": at_top_songs[9][1],
    "at_song1artist": at_top_songs[0][3],
    "at_song2artist": at_top_songs[1][3],
    "at_song3artist": at_top_songs[2][3],
    "at_song4artist": at_top_songs[3][3],
    "at_song5artist": at_top_songs[4][3],
    "at_song6artist": at_top_songs[5][3],
    "at_song7artist": at_top_songs[6][3],
    "at_song8artist": at_top_songs[7][3],
    "at_song9artist": at_top_songs[8][3],
    "at_song10artist": at_top_songs[9][3],
    "at_song1count": at_top_songs[0][6],
    "at_song2count": at_top_songs[1][6],
    "at_song3count": at_top_songs[2][6],
    "at_song4count": at_top_songs[3][6],
    "at_song5count": at_top_songs[4][6],
    "at_song6count": at_top_songs[5][6],
    "at_song7count": at_top_songs[6][6],
    "at_song8count": at_top_songs[7][6],
    "at_song9count": at_top_songs[8][6],
    "at_song10count": at_top_songs[9][6],
    "at_artist1": at_top_artists[0][3],
    "at_artist2": at_top_artists[1][3],
    "at_artist3": at_top_artists[2][3],
    "at_artist4": at_top_artists[3][3],
    "at_artist5": at_top_artists[4][3],
    "at_artist6": at_top_artists[5][3],
    "at_artist7": at_top_artists[6][3],
    "at_artist8": at_top_artists[7][3],
    "at_artist9": at_top_artists[8][3],
    "at_artist10": at_top_artists[9][3],
    "at_artist1cover": get_artist_image_from_song_id(at_top_albums[0][0]),
    "at_artist2cover": get_artist_image_from_song_id(at_top_albums[1][0]),
    "at_artist3cover": get_artist_image_from_song_id(at_top_albums[2][0]),
    "at_artist4cover": get_artist_image_from_song_id(at_top_albums[3][0]),
    "at_artist5cover": get_artist_image_from_song_id(at_top_albums[4][0]),
    "at_artist6cover": get_artist_image_from_song_id(at_top_albums[5][0]),
    "at_artist7cover": get_artist_image_from_song_id(at_top_albums[6][0]),
    "at_artist8cover": get_artist_image_from_song_id(at_top_albums[7][0]),
    "at_artist9cover": get_artist_image_from_song_id(at_top_albums[8][0]),
    "at_artist10cover": get_artist_image_from_song_id(at_top_albums[9][0]),
    "at_album1": at_top_albums[0][2],
    "at_album2": at_top_albums[1][2],
    "at_album3": at_top_albums[2][2],
    "at_album4": at_top_albums[3][2],
    "at_album5": at_top_albums[4][2],
    "at_album6": at_top_albums[5][2],
    "at_album7": at_top_albums[6][2],
    "at_album8": at_top_albums[7][2],
    "at_album9": at_top_albums[8][2],
    "at_album10": at_top_albums[9][2],
    "at_album1cover": at_top_albums[0][5],
    "at_album2cover": at_top_albums[1][5],
    "at_album3cover": at_top_albums[2][5],
    "at_album4cover": at_top_albums[3][5],
    "at_album5cover": at_top_albums[4][5],
    "at_album6cover": at_top_albums[5][5],
    "at_album7cover": at_top_albums[6][5],
    "at_album8cover": at_top_albums[7][5],
    "at_album9cover": at_top_albums[8][5],
    "at_album10cover": at_top_albums[9][5],
}

# Path to the HTML template file
template_path = os.path.join(script_dir, 'email.html')

# Generate the HTML content with replacements
html_content = generate_html_from_template(template_path, replacements)

# Send the email with the generated HTML content
send_html_email("Spotipy Wrapped", html_content, "imacdonald135@gmail.com")