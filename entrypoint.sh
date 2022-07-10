#!/bin/sh
set -e

python3 manage.py makemigrations MomentumBackend

python3 manage.py migrate MomentumBackend --fake-initial

if [ -z "$MOMENTUM_TEST" ]; then
  python3 manage.py runserver 0.0.0.0:8000
else
  python3 manage.py test
fi
