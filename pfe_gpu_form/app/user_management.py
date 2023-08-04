import queue
import subprocess
import time
import threading
import signal
import os
import shutil

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from datetime import datetime, timedelta
from django.utils import timezone

from .models import SessionRequest, Etudiant

def get_schedule(session_choice):
    # Define the session timings
    morning_start = timedelta(hours=7)
    morning_end = timedelta(hours=14)
    afternoon_start = timedelta(hours=14, minutes=30)
    afternoon_end = timedelta(hours=23, minutes=59)

    # Get the last session for the chosen type
    latest_session = SessionRequest.objects.filter(session_choice=session_choice).order_by('-date_debut').first()

    # Calculate the next available date_debut and date_fin based on the latest session
    date_debut = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    if latest_session and latest_session.date_fin.date() >= date_debut.date():
        date_debut = latest_session.date_fin + timedelta(days=1)

    if session_choice == 'Matinale':
        date_debut += morning_start
        date_fin = date_debut + morning_end - morning_start
    else:
        date_debut += afternoon_start
        date_fin = date_debut + afternoon_end - afternoon_start

    return date_debut, date_fin


def create_user(username, password):
    subprocess.run(['useradd', '-m', username], check=True)
    subprocess.run(['chpasswd'], input=f'{username}:{password}', universal_newlines=True, check=True)
    subprocess.run(['passwd', '-l', f'{username}'], check=True)

def close_session_user(username):
    try:
        subprocess.run(['pkill', '-u', username], check=False)
        # lock the user's password
        subprocess.run(['passwd', '-l', f'{username}'], check=True)
    except subprocess.CalledProcessError:
        print(f"No running processes found for {username}, user session already closed.")
    else:
        print(f"All processes for {username} have been terminated, user session closed.")

def start_session(etudiant_id, session_request_id):
    session_request = SessionRequest.objects.get(id=session_request_id)

    # while the session date_debut is not reached, wait
    while timezone.now() < session_request.date_debut:
        time.sleep(1)
    
    etudiant = Etudiant.objects.get(id=etudiant_id)
    #unlock the user's password
    subprocess.run(['passwd', '-u', f'{etudiant.email}'], check=True)
    print(f'User {etudiant.email}\'s password has been unlocked.')

    # Calculate the delay to notify the user 30 minutes before session ends
    notify_delay = (session_request.date_fin - timezone.now()).total_seconds() - 1800  # 1800 seconds = 30 minutes

    # Start the thread to notify the user
    threading.Thread(target=notify_user, args=(notify_delay, "Session Ending Soon", "Your session will end in 30 minutes. Please save your work.", 5000)).start()

    # Wait until the session end time
    delay = (session_request.date_fin - timezone.now()).total_seconds()
    time.sleep(delay)

    # Close the session
    close_session_user(etudiant.email)
    print(f'User {etudiant.email}\'s session ended successfully and password locked.')


def notify_user(notify_delay, title, message, duration=5000):
    time.sleep(notify_delay)
    try:
        subprocess.run(['notify-send', '--expire-time', str(duration), title, message])
        print(f"Notification sent: {title} - {message}")
    except Exception as e:
        print(f"Failed to send notification: {str(e)}")



def send_email(username, subject, body):
    from_email = "reseau@esi.dz"
    to_email = username
    password = "D@t@ C3nt3r@1969"

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
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

def send_email_delayed(username, subject, body, time_delay, end_time):
    if timezone.now() == end_time - time_delay:
        send_email(username, subject, body)








