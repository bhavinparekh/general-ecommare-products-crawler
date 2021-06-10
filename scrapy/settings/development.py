import os
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
env.read_env('.env')
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")
# CORSALLOWALLORIGINSL False
# if env("CORS_ALLOW_ALL_ORIGINS") == "True":
#     CORSALLOWALLORIGINSL True

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
CORS_ALLOW_ALL_ORIGINS = True

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
