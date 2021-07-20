# Cagnotte Solidaire

[![Tests](https://github.com/caracole-io/cagnottesolidaire/actions/workflows/test.yml/badge.svg)](https://github.com/caracole-io/cagnottesolidaire/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/caracole-io/cagnottesolidaire/branch/master/graph/badge.svg?token=BLGISGCYKG)](https://codecov.io/gh/caracole-io/cagnottesolidaire)

## Reverse Proxy

This app needs træefik, eg. [proxyta.net](https://framagit.org/oxyta.net/proxyta.net)

## Dev

```
echo POSTGRES_PASSWORD=$(openssl rand -base64 32) >> .env
echo SECRET_KEY=$(openssl rand -base64 32) >> .env
echo DEBUG=True >> .env
. .env
docker-compose up -d --build
```

You may then want to create an admin: `docker-compose exec app ./manage.py createsuperuser`
