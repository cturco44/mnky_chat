web: gunicorn --bind :8000 --workers 3 --threads 2 mnky_chat.wsgi:application
websocket: daphne -b :: -p 5000 mnky_chat.asgi:application