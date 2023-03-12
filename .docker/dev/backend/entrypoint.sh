#!/bin/sh

# Install package
pip install -r requirements/dev.txt

until python manage.py check --database default
do
    echo "Check DB Connection ..."
    sleep 5
done

until python manage.py makemigrations --check --dry-run
do
    echo "Check DB"
    sleep 7
done


until python manage.py migrate
do
    echo "Waiting for db to be ready..."
    sleep 7
done

# Collect static
python manage.py collectstatic --no-input

#chmod 755 staticfiles
# Create Super User
#python manage.py createsuperuser --noinput

# load zip codes
#python manage.py load_uk_zip_code

# Start Server for gunicorn
#gunicorn core.wsgi --bind 0.0.0.0:8000 --workers 4 --threads 4

# for debug
python manage.py runserver 0.0.0.0:8000

exec "$@"
