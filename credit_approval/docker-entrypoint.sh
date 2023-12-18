#!/bin/bash
set -e

# Apply database migrations
python manage.py migrate

# Create a default superuser if it doesn't exist
echo "from django.contrib.auth.models import User; User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', '', 'admin')" | python manage.py shell

# Start the Django development server
# exec "$@"
python manage.py runserver 0.0.0.0:8000
