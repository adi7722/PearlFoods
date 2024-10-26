@echo off
echo "BUILD START"

REM Install dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

REM Collect static files
python manage.py collectstatic --noinput --clear

echo "BUILD END"
