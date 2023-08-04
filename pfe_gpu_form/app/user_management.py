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

session_queue = queue.Queue()  # Create a FIFO queue

from datetime import datetime, timedelta, timezone

from .models import SessionRequest, Etudiant

def get_schedule(session_choice):
    # Define the session timings
    morning_start = timedelta(hours=7)
    morning_end = timedelta(hours=14)
    afternoon_start = timedelta(hours=14, minutes=30)
    afternoon_end = timedelta(hours=23, minutes=59)

    # Find the latest session for the chosen type
    latest_session = SessionRequest.objects.filter(session_choice=session_choice).order_by('-date_debut').first()

    # Calculate the next available date_debut and date_fin based on the latest session
    date_debut = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    if latest_session and latest_session.date_debut.date() >= date_debut.date():
        date_debut = latest_session.date_debut + timedelta(days=1)

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
    except subprocess.CalledProcessError:
        print(f"No running processes found for {username}, user session already closed.")
    else:
        print(f"All processes for {username} have been terminated, user session closed.")

def manage_user(username, password, session_type):
    date_debut, date_fin = get_schedule(session_type)
    create_user(username, password)

    # Wait until the session start time
    delay = (date_debut - datetime.now()).total_seconds()
    time.sleep(delay)
    subject = "Informations sur votre demande de session GPU"
    body = f"Bonjour {username} !\n\nNous vous informons que votre session sera disponible à partir de {date_debut.strftime('%H:%M')} et sera active jusqu'à {date_fin.strftime('%H:%M')}.\n\n Nous vous rappelons que votre mot de passe est {password}.\n\nCordialement,\nService Réseaux ESI"
    send_email(username, subject, body)
    # Schedule a thread to notify user 30 minutes before session ends
    notify_delay = (date_fin - datetime.now()).total_seconds() - 1800  # 1800 seconds = 30 minutes
    threading.Thread(target=notify_user, args=(notify_delay,"Session Ending Soon", "Your session will end in 30 minutes. Please save your work.", 5000)).start()
        # Wait until the session end time
    delay = (date_fin - datetime.now()).total_seconds()
    time.sleep(delay)
        # Close session
    close_session_user(username)

def notify_user(notify_delay, title, message, duration=5000):
    time.sleep(notify_delay)
    try:
        subprocess.run(['notify-send', '--expire-time', str(duration), title, message])
        print(f"Notification sent: {title} - {message}")
    except Exception as e:
        print(f"Failed to send notification: {str(e)}")


def redemand_session(username, password, session_type):
    # Unlock the user's password
    subprocess.run(['passwd', '-u', f'{username}'], check=True)
    print(f'User {username}\'s password has been unlocked.')

    # Get the schedule for this user
    date_debut, date_fin = get_schedule(session_type)

    # Notify the user about the new session details
    subject = "Informations sur votre demande de session GPU"
    body = f"Bonjour {username},\n\nVotre nouvelle session GPU a été programmé pour {date_debut} et sera automatiquement arreté le {date_fin}.\n\n Nous vous rappelons que votre mot de passe est {password}.\n\nCordialement,\nService Réseaux ESI"
    send_email(username, subject, body)

    # Calculate the delay to notify the user 30 minutes before session ends
    notify_delay = (date_fin - datetime.now()).total_seconds() - 1800  # 1800 seconds = 30 minutes

    # Start the thread to notify the user
    threading.Thread(target=notify_user, args=(notify_delay, "Session Ending Soon", "Your session will end in 30 minutes. Please save your work.", 5000)).start()

    # Wait until the session end time
    delay = (date_fin - datetime.now()).total_seconds()
    time.sleep(delay)

    # Close the session
    close_session_user(username)
    print(f'User {username}\'s session ended successfully.')


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








