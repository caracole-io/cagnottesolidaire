# Cagnotte Solidaire
[![Build Status](https://travis-ci.org/caracole-io/cagnottesolidaire.svg?branch=master)](https://travis-ci.org/caracole-io/cagnottesolidaire)
[![Coverage Status](https://coveralls.io/repos/github/caracole-io/cagnottesolidaire/badge.svg?branch=master)](https://coveralls.io/github/caracole-io/cagnottesolidaire?branch=master)

## Reverse Proxy

This app needs a reverse proxy, like [proxyta.net](https://framagit.org/nim65s/proxyta.net)

## Dev

Make sure `cagnottesolidaire.local` resolves to `localhost`, and:

```
echo POSTGRES_PASSWORD=$(openssl rand -base64 32) >> .env
echo SECRET_KEY=$(openssl rand -base64 32) >> .env
echo DEBUG=True >> .env
. .env
docker-compose up -d --build
```

You may then want to create an admin: `docker-compose exec app ./manage.py createsuperuser`
