#! /bin/sh

python -m venv venv
source venv/bin/activate
# pip install wheel
pip install flask
pip install flask_cors
# pip install gunicorn flask
export FLASK_APP=./core/app
# export FLASK_ENV=development
export FLASK_DEBUG=true
# sudo ufw allow 5000
# gunicorn --bind 0.0.0.0:5000 wsgi:app
flask run