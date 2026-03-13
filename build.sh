#!/usr/bin/env bash

pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata data.json
python manage.py collectstatic --noinput