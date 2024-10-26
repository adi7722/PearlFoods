#!/bin/bash

echo "BUILD START"

# Export database environment variable for Django to use PostgreSQL
export DATABASE_URL="postgres://admin_pearl_foods:MOH9e]52>0@h4l%@localhost:5432/PearlFoods"

# Upgrade pip and install dependencies
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

# Collect static files
python3 manage.py collectstatic --noinput --clear

echo "BUILD END"
