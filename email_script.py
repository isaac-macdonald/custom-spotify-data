import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

load_dotenv()

def send_html_email(subject, body, to_email):
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
        html_content = html_content.replace(f"{{{{ {placeholder} }}}}", value)
    print(html_content )
    return html_content

# Replace these values with actual data
replacements = {
    "name": "John",
    "color": "blue"
}

# Path to the HTML template file
template_path = "email.html"

# Generate the HTML content with replacements
html_content = generate_html_from_template(template_path, replacements)

# Send the email with the generated HTML content
send_html_email("Personalized HTML Email", html_content, "imacdonald135@gmail.com")