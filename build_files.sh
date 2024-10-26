#!/bin/bash

echo "BUILD START"

# Set environment variables for PostgreSQL database
export DATABASE_URL="postgres://admin_pearl_foods:MOH9e]52>0@h4l%@localhost:5432/PearlFoods"
export DATABASE_USER="admin_pearl_foods"
export DATABASE_PASSWORD="MOH9e]52>0@h4l%"
export DATABASE_NAME="PearlFoods"
export DATABASE_HOST="localhost"
export DATABASE_PORT="5432"

# Add the Python script directory to PATH for any necessary executables
export PATH=$PATH:/python312/bin

# Upgrade pip and install dependencies
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt --no-warn-script-location

# Run database migrations and collect static files
python3 manage.py migrate
python3 manage.py collectstatic --noinput --clear

echo "BUILD END"
