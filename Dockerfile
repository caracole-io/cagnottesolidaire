FROM python:3.6-alpine

EXPOSE 8000

RUN mkdir /app
WORKDIR /app


RUN apk update -q && apk add -q --no-cache \
    py-pillow \
    py3-psycopg2 \
 && pip3 install --no-cache-dir \
    gunicorn \
    pipenv \
    python-memcached

ENV PYTHONPATH=/usr/lib/python3.6/site-packages
RUN rm /usr/local/bin/pip3 /usr/local/bin/pip

ADD Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy

ADD . .

CMD while ! nc -z postgres 5432; do sleep 1; done \
 && ./manage.py migrate \
 && ./manage.py collectstatic --no-input \
 && gunicorn \
    --bind 0.0.0.0 \
    testproject.wsgi
