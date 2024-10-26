echo : "BUILD START"

python 3.12.4 python -m pip install -r requirements.txt
python 3.12.4 manage.py collectstatic --noinput --clear

echo : "BUILD END"