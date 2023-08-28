## Django-Celery-Redis Ticketing System

This project leverages the power of Django, Celery, and Redis to manage user sessions on a high-performance machine. Users can acquire tickets (comprising a username and password) and the system adeptly handles session management tasks such as initiation, locking, and termination.

Homepage and form for ticket access:

Features

- User Ticketing: Acquire access to a high-performance machine through a ticket system.
- Session Management: Start, lock, and end sessions with seamless orchestration using Celery.
- High Concurrency: Built for performance with the robust capabilities of Celery and Redis.

Prerequisites

    Python 3.x
    Django
    Redis Server
    Celery

Installation

    Clone the repository:

    git clone <repository_link>

Navigate to the project directory and install the requirements:

    cd project_directory
    pip install -r requirements.txt

Run migrations:


    python manage.py migrate

Start the Django development server:

    python manage.py runserver

Using Celery with Redis

To harness the full power of this system, ensure the Redis server is running and then start the Celery worker:

    celery -A your_project_name worker --loglevel=info

For real-time task monitoring, you can utilize Flower:


    celery -A your_project_name flower

## Contributing

Feel free to fork the project, create a feature branch, and send us a pull request.
