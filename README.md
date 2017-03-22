# Cagnotte Solidaire
[![Build Status](https://travis-ci.org/nim65s/cagnottesolidaire.svg?branch=master)](https://travis-ci.org/nim65s/cagnottesolidaire)
[![Coverage Status](https://coveralls.io/repos/github/nim65s/cagnottesolidaire/badge.svg?branch=master)](https://coveralls.io/github/nim65s/cagnottesolidaire?branch=master)


## Dev
```
vf new cagnottesolidaire
vf connect
pip install -r requirements.txt
sudo mkdir -p /etc/django/cangottesolidaire
sudo chown $USER /etc/django/cangottesolidaire
echo pipo > /etc/django/cagnottesolidaire/secret_key.txt
echo pipo > /etc/django/cagnottesolidaire/email_password
./manage.py migrate
./manage.py createsuperuser --email guilhem@saurel.me --username nim
./manage.py runserver
```
