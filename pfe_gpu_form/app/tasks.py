from celery import shared_task
from datetime import datetime, timedelta
import pytz
from .models import Etudiant, SessionRequest
import subprocess

from celery import shared_task
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

@shared_task
def create_user_task(username, password):
    subprocess.run(['useradd', '-m', username], check=True)
    subprocess.run(['chpasswd'], input=f'{username}:{password}', universal_newlines=True, check=True)
    subprocess.run(['passwd', '-l', f'{username}'], check=True)


@shared_task
def send_email_task(username, subject, body):
    from_email = "reseau@esi.dz"
    password = "D@t@ C3nt3r@1969"

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = username
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(from_email, password)
        server.send_message(msg)
        server.quit()
        print(f"Email sent to {username}")
    except Exception as e:
        print(f"Failed to send email to {username}: {str(e)}")

@shared_task
def notify_user(title, message, duration=5000):
    try:
        subprocess.run(['notify-send', '--expire-time', str(duration), title, message])
        print(f"Notification sent: {title} - {message}")
    except Exception as e:
        print(f"Failed to send notification: {str(e)}")

@shared_task
def close_session_user(username):
    try:
        subprocess.run(['pkill', '-u', username], check=False)
        # lock the user's password
        subprocess.run(['passwd', '-l', f'{username}'], check=True)
    except subprocess.CalledProcessError:
        print(f"No running processes found for {username}, user session already closed.")
    else:
        print(f"All processes for {username} have been terminated, user session closed.")

@shared_task
def start_user_session(etudiant_id, session_request_id):
    session_request = SessionRequest.objects.get(id=session_request_id)
    etudiant = Etudiant.objects.get(id=etudiant_id)

    print(f'Starting session for {etudiant.email}')
    subprocess.run(['passwd', '-u', f'{etudiant.email}'], check=True)
    print(f'User {etudiant.email}\'s password has been unlocked.')

    # Calculate time left until 30 minutes before session ends and trigger a notification
    notify_delay = session_request.date_fin - timedelta(minutes=30)
    notify_user.apply_async(args=["Session Ending Soon","Your session will end in 30 minutes. Please save your work."], eta=notify_delay)

    # End the user session at session's end time
    close_session_user.delay(etudiant.email)

    