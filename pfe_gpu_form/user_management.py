import subprocess
import time
import threading
import signal
import os

import shutil

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class LoginEventHandler(FileSystemEventHandler):
    def __init__(self, username, password, session_length):
        self.username = username
        self.password = password
        self.session_length = session_length

    def on_modified(self, event):
        if event.src_path == '/var/log/auth.log':
            with open('/var/log/auth.log', 'r') as f:
                if f"session opened for user {self.username}" in f.read():
                    print(f'User {self.username} logged in, they will be deleted in {self.session_length} ...')
                    time.sleep(self.session_length)
                    delete_user(self.username)
                    print(f'User {self.username} deleted.')
                    self.stop()

    def stop(self):
        self.stopped = True

def create_user(username, password):
    subprocess.run(['useradd', '-m', username], check=True)
    subprocess.run(['chpasswd'], input=f'{username}:{password}', universal_newlines=True, check=True)

def delete_user(username):
    try:
        subprocess.run(['pkill', '-u', username], check=True)
    except subprocess.CalledProcessError:
        print(f"No running processes for {username}, continuing with deletion.")
    subprocess.run(['userdel', '-r', username], check=True)

def manage_user(username, password, session_length):
    total, used, free = shutil.disk_usage("/")

    # Convert free space to GB
    free_gb = free // (2**30)

    if free_gb < 10:  # If less than 10 GB is free
        print("Insufficient disk space. Need at least 10GB free.")
        return

    create_user(username, password)

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




def main(): # just for testing
    username = 'testuser'
    password = 'password'
    session_length = 10  # 10 seconds for testing

    # Start a new thread to manage the user
    threading.Thread(target=manage_user, args=(username, password, session_length)).start()

    # The script can continue with other tasks here
    print('Doing other tasks...')


