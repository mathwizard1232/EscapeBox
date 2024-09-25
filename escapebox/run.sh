#!/bin/bash

# Activate the virtual environment
source venv/bin/activate

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Run the Django development server
python manage.py runserver