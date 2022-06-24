FROM python:latest

# load data
COPY . /app/

# change cwd to app
WORKDIR /app

# install requirements
RUN pip install -r requirements.txt

# create migrations
RUN python manage.py makemigrations

# excute the entrypoint.sh file
ENTRYPOINT ["./entrypoint.sh"]
