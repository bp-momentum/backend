#!/bin/sh
set -e

python3 manage.py makemigrations MomentumBackend

python3 manage.py migrate MomentumBackend

python3 manage.py runserver 0.0.0.0:8000