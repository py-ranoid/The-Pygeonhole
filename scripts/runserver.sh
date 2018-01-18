#!/bin/sh

# ADD YOUR COMMANDS BELOW

# First, makemigrations and migrate
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic

# Your commands
# Eg: python3 manage.py collectstatic --noinput etc

# DO NOT ADD ANY COMMANDS BELOW THIS LINE
# Now run the gunicorn server
gunicorn --config /conf/gunicorn_config.py exp.wsgi
