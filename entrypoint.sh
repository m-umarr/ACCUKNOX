#!/bin/sh

# Apply database migrations
python manage.py migrate

# Start the development server
exec "$@"