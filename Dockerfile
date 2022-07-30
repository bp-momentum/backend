FROM python:latest

RUN apt-get update && \
    apt-get install -y locales && \
    sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales

ENV LANG en_US.utf8
ENV LC_ALL en_US.utf8

ARG DATABASE_NAME=momentum
ARG DATABASE_USER=momentum
ARG DATABASE_PASSWORD=momentum
ARG DATABASE_HOST=momentum-db  # this needs to be the container name of the db
ARG DATABASE_PORT=5432

ENV EMAIL_ADDRESS test@example.com
ENV EMAIL_PASSWORD test
ENV EMAIL_HOST smtp.example.com
ENV VIDEO_PATH videos
ENV ALLOWED_ORIGINS http://localhost
ENV ALLOWED_HOSTS http://localhost
ENV WEBSITE_URL localhost:8080

# load data
COPY . /app/

# change cwd to app
WORKDIR /app

# install requirements
RUN pip install -r requirements.txt

# make entrypoint executable
RUN chmod +x entrypoint.sh

EXPOSE 8000

# excute the entrypoint.sh file
ENTRYPOINT ["./entrypoint.sh"]
