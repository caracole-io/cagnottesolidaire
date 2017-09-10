# Cagnotte Solidaire
[![Build Status](https://travis-ci.org/nim65s/cagnottesolidaire.svg?branch=master)](https://travis-ci.org/nim65s/cagnottesolidaire)
[![Coverage Status](https://coveralls.io/repos/github/nim65s/cagnottesolidaire/badge.svg?branch=master)](https://coveralls.io/github/nim65s/cagnottesolidaire?branch=master)

## Deploy

- `pip install -e git://github.com/Nim65s/cagnottesolidaire.git#egg=cagnottesolidaire `

- add those lines to your `INSTALLED_APPS` in `settings.py`:

```
    'cagnottesolidaire',
    'django.contrib.humanize',
    'django.contrib.sites',
    'bootstrap3',  # only if you want to use the provided templates
```
- add `SITE_ID = 1` to `settings.py`
- add `    url(r'^cagnottesolidaire/', include('cagnottesolidaire.urls')),` to your `urlpatterns` in `urls.py`


## Dev
```
vf new cagnottesolidaire
vf connect
pip install -r requirements.txt
./manage.py migrate
./manage.py createsuperuser --email guilhem@saurel.me --username nim
./manage.py runserver
```
