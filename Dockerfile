FROM python:slim

EXPOSE 8000

RUN mkdir /app
WORKDIR /app

RUN apt-get update -qqy \
 && apt-get install -qqy \
    gcc \
    libpq-dev \
    netcat \
 && pip3 install --no-cache-dir -U pip \
 && pip3 install --no-cache-dir \
    gunicorn \
    pipenv \
    psycopg2 \
    python-memcached \
 && apt-get autoremove -qqy gcc \
 && rm -rf /var/lib/apt/lists/*

ADD Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy

ADD . .

CMD while ! nc -z postgres 5432; do sleep 1; done \
 && ./manage.py migrate \
 && ./manage.py collectstatic --no-input \
 && gunicorn \
    --bind 0.0.0.0 \
    testproject.wsgi
