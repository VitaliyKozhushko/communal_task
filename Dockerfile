FROM python:3.10-alpine

# install psycopg2 dependencies
RUN apk add --update --no-cache --virtual .tmp-build-deps \
        libpq-dev gcc postgresql-dev python3-dev

# set work directory
WORKDIR /project

# install dependencies
COPY requirements.txt /project/
RUN pip install --no-cache-dir -r requirements.txt

# copy project
COPY . .

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
