import os

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")
# CORSALLOWALLORIGINSL False
# if os.getenv("CORS_ALLOW_ALL_ORIGINS") == "True":
#     CORSALLOWALLORIGINSL True

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS_PROD").split(',')
CORS_ALLOW_ALL_ORIGINS = True
