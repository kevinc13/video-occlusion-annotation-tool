"""
Django settings
"""

import os, json
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# -----------------------------------------------------------------------------
# Load environment configuration
# 
# Default path for env file is this project directory
# Otherwise, we'll use the path set by an environment variable
# -----------------------------------------------------------------------------
ENV_FILE = os.environ.get(
    "DJANGO_ENV_FILE", default=os.path.join(BASE_DIR, "project/env.json"))
with open(ENV_FILE) as f:
    env_data = json.load(f)

def env(key, default=None):
    """
    Retrieves environment variable if set, otherwise 
    returns a default value or raises an error
    """
    if key in env_data:
        value = env_data[key]
        if value == "True":
            return True
        elif value == "False":
            return False
        return value
    elif default is not None:
        return default
    else:
        raise ImproperlyConfigured(
            "ImproperlyConfigured: Environment variable {} has not been set"
            .format(key))

# Name of the environment (e.g. dev, testing, production)
ENV_NAME = env("ENV_NAME")

# -----------------------------------------------------------------------------
# Security Settings
# -----------------------------------------------------------------------------
SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG", False)
ALLOWED_HOSTS = env("ALLOWED_HOSTS", [])

# -----------------------------------------------------------------------------
# Application Definition
# -----------------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'webpack_loader',
    'api.apps.ApiConfig'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'

# -----------------------------------------------------------------------------
# Database
# -----------------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env("DB_NAME"),
        'USER': env("DB_USER"),
        'PASSWORD': env("DB_PASSWORD"),
        'HOST': env("DB_HOST", "127.0.0.1")
    }
}

# -----------------------------------------------------------------------------
# Password Validation
# -----------------------------------------------------------------------------
LOGIN_URL = "/"
LOGIN_REDIRECT_URL = "/app"
LOGOUT_REDIRECT_URL = "/"

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = "api.User"

# -----------------------------------------------------------------------------
# Internalization
# -----------------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# -----------------------------------------------------------------------------
# Media Files
# -----------------------------------------------------------------------------
MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), "media")
MEDIA_URL = "/media/"

# -----------------------------------------------------------------------------
# Static Files (i.e. CSS, images, JavaScript)
# -----------------------------------------------------------------------------

# Directories to look for when collecting static files
# Note: We include both the Webpack compiled static files from the frontend
#       as well as any shared static files between frontend and backend
STATICFILES_DIRS = [
    os.path.join(os.path.dirname(BASE_DIR), 'frontend/dist'),
    os.path.join(os.path.dirname(BASE_DIR), "shared_static")    
]

# URL endpoint for accessing static files
STATIC_URL = '/static/'

# Directory where collected static files will reside
# Note: the actual directory where the files reside may be different
# from the URL path used to access them!
STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'public')

# Configure the Webpack loader plugin
WEBPACK_LOADER = {
    "DEFAULT": {
        "BUNDLE_DIR_NAME": "",
        "STATS_FILE": os.path.join(
            os.path.dirname(BASE_DIR), "frontend/webpack-stats.json")
    }
}
