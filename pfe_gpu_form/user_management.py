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

class LoginEventHandler(FileSystemEventHandler):
    def __init__(self, username, password, session_length):
        self.username = username
        self.password = password
        self.session_length = session_length

    def on_modified(self, event):
        if event.src_path == '/var/log/auth.log':
            with open('/var/log/auth.log', 'r') as f:
                if f"session opened for user {self.username}" in f.read():
                    print(f'User {self.username} logged in, their session will be stopped in {self.session_length} seconds')
                    time.sleep(self.session_length)
                    close_session_user(self.username)
                    print(f'User {self.username}\'s session stopped successfully.')
                    subprocess.run(['passwd', '-l', f'{self.username}'], check=True)
                    print(f'User {self.username}\'s password has been locked.')
                    session_queue.get()  # Remove this session from the queue
                    self.stop()

    def stop(self):
        self.stopped = True

def create_user(username, password):
    subprocess.run(['useradd', '-m', username], check=True)
    subprocess.run(['chpasswd'], input=f'{username}:{password}', universal_newlines=True, check=True)

def close_session_user(username):
    try:
        subprocess.run(['pkill', '-u', username], check=False)
    except subprocess.CalledProcessError:
        print(f"No running processes found for {username}, user session already closed.")
    else:
        print(f"All processes for {username} have been terminated, user session closed.")

def manage_user(username, password, session_length):
    
    subject_processing = "Demande de session en cours de traitement"
    body_processing = f"Bonjour {username},\n\nVotre demande de session GPU est actuellement en attente dans notre file d'attente. Nous vous informerons dès que votre session sera prête.\n\nCordialement,\nService Réseaux ESI"
    send_email(username, subject_processing, body_processing)

    while not session_queue.empty():  # Wait until the queue is empty
        time.sleep(1)

    total, used, free = shutil.disk_usage("/")
    free_gb = free // (2**30)
    if free_gb < 10:
        print("Insufficient disk space. Need at least 10GB free.")
        return

    create_user(username, password)
    session_queue.put(username)  # Add this session to the queue
    subject = "Nouvelle session créée"
    body = f"Bonjour {username},\n\nNous avons reçu votre demande de création de session GPU. Nous vous offrons une session qui va durer {session_length % 3600} heures. Veuillez vous connecter à la machine GPU en utilisant:\nUsername: {username}\nPassword: {password}\n\nBon Courage !,\nService Réseaux ESI"
    send_email(username, subject, body)

    event_handler = LoginEventHandler(username, password, session_length)
    observer = Observer()
    observer.schedule(event_handler, '/var/log/', recursive=False)
    observer.start()

    try:
        while observer.is_alive():
            observer.join(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def redemand_session(username, password, session_length):
    subprocess.run(['passwd', '-u', f'{username}'], check=True)
    print(f'User {username}\'s password has been unlocked.')
    event_handler = LoginEventHandler(username, password, session_length)
    observer = Observer()
    observer.schedule(event_handler, '/var/log/', recursive=False)
    observer.start()

    try:
        while observer.is_alive():
            observer.join(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    print(f'User {username}\'s session created successfully.')


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






