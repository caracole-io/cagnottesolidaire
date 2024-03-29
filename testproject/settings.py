"""Settings for Cagnotte Solidaire's test project."""
import os

PROJECT = "cagnottesolidaire"
PROJECT_VERBOSE = "Cagnotte Solidaire"

DOMAIN_NAME = os.environ.get("DOMAIN_NAME", "localhost")
HOSTNAME = os.environ.get("ALLOWED_HOST", f"{PROJECT}.{DOMAIN_NAME}")
ALLOWED_HOSTS = [HOSTNAME]
ALLOWED_HOSTS += [f"www.{host}" for host in ALLOWED_HOSTS]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.environ.get("SECRET_KEY", "pipo")
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

INSTALLED_APPS = [
    PROJECT,
    "ndh",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.contrib.sites",
    "bootstrap4",
    "testproject",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "testproject.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "testproject.wsgi.application"

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DB = os.environ.get("DB", "db.sqlite3")
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, DB),
    },
}
if DB == "postgres":
    DATABASES["default"].update(
        ENGINE="django.db.backends.postgresql",
        NAME=os.environ.get("POSTGRES_DB", DB),
        USER=os.environ.get("POSTGRES_USER", DB),
        HOST=os.environ.get("POSTGRES_HOST", DB),
        PASSWORD=os.environ["POSTGRES_PASSWORD"],
    )

_APV = "django.contrib.auth.password_validation"
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": f"{_APV}.UserAttributeSimilarityValidator",
    },
    {
        "NAME": f"{_APV}.MinimumLengthValidator",
    },
    {
        "NAME": f"{_APV}.CommonPasswordValidator",
    },
    {
        "NAME": f"{_APV}.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = os.environ.get("LANGUAGE_CODE", "fr")
TIME_ZONE = os.environ.get("TIME_ZONE", "Europe/Paris")
USE_I18N = True
USE_TZ = True

SITE_ID = int(os.environ.get("SITE_ID", 1))

MEDIA_ROOT = "/srv/media/"
MEDIA_URL = "/media/"
STATIC_URL = "/static/"
STATIC_ROOT = "/srv/static/"
LOGIN_REDIRECT_URL = "/"

if os.environ.get("MEMCACHED", "False").lower() == "true":
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
            "LOCATION": "memcached:11211",
        },
    }
