#!/bin/bash

echo "BUILD START"

# Upgrade pip and install dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput --clear

echo "BUILD END"
