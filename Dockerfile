FROM python:slim

EXPOSE 8000

WORKDIR /app

ENV PYTHONUNBUFFERED=1

CMD while ! nc -z postgres 5432; do sleep 1; done \
 && ./manage.py migrate \
 && ./manage.py collectstatic --no-input \
 && gunicorn \
    --bind 0.0.0.0 \
    testproject.wsgi

RUN apt-get update -qqy \
 && apt-get install -qqy \
    gcc \
    libpq-dev \
    netcat \
 && pip3 install --no-cache-dir -U pip \
 && pip3 install --no-cache-dir \
    gunicorn \
    poetry \
    psycopg2 \
    python-memcached \
    raven \
    requests \
 && apt-get autoremove -qqy gcc \
 && rm -rf /var/lib/apt/lists/*

ADD pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false --local \
 && poetry install --no-dev --no-root --no-interaction --no-ansi

ADD . .
