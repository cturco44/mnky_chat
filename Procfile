web: gunicorn --bind :8000 --workers 3 --threads 2 <project_name>.wsgi:application
websocket: daphne -b :: -p 5000 <project_name>.asgi:application