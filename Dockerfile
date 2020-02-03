FROM alpine:3.11

EXPOSE 8000

RUN mkdir /app
WORKDIR /app

RUN apk update -q && apk add -q --no-cache \
    py3-psycopg2 \
 && pip3 install --no-cache-dir -U pip \
 && pip3 install --no-cache-dir \
    gunicorn \
    pipenv \
    python-memcached

ADD Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy

ADD . .

CMD while ! nc -z postgres 5432; do sleep 1; done \
 && ./manage.py migrate \
 && ./manage.py collectstatic --no-input \
 && gunicorn \
    --bind 0.0.0.0 \
    testproject.wsgi
