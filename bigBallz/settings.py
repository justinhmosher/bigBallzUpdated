"""
Django settings for bigBallz project.

Generated by 'django-admin startproject' using Django 2.2.28.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
from pathlib import Path
from.info import *


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EMAIL_USE_TLS = EMAIL_USE_TLS
EMAIL_HOST = EMAIL_HOST
EMAIL_HOST_USER = EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = EMAIL_HOST_PASSWORD
EMAIL_PORT = EMAIL_PORT

# settings.py
#CSRF_FAILURE_VIEW = 'authentication.views.custom_csrf_failure_view'

SESSION_COOKIE_SECURE = True  # Ensures cookies are only sent over HTTPS
SESSION_COOKIE_AGE = 2592000  # Default session age set to 30 days (for cases when not overridden)
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Prevents session from expiring

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
from django.core.management.utils import get_random_secret_key
from decouple import config

SECRET_KEY = get_random_secret_key()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'authentication',
    'authentication.NFL_weekly_view',
    'authentication.baseball_SL',
    'authentication.baseball_WL',
    'django.contrib.sitemaps',
    'channels',
    'django_ckeditor_5',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

CKEDITOR_UPLOAD_PATH = "uploads/"

customColorPalette = [
      {
          'color': 'hsl(4, 90%, 58%)',
          'label': 'Red'
      },
      {
          'color': 'hsl(340, 82%, 52%)',
          'label': 'Pink'
      },
      {
          'color': 'hsl(291, 64%, 42%)',
          'label': 'Purple'
      },
      {
          'color': 'hsl(262, 52%, 47%)',
          'label': 'Deep Purple'
      },
      {
          'color': 'hsl(231, 48%, 48%)',
          'label': 'Indigo'
      },
      {
          'color': 'hsl(207, 90%, 54%)',
          'label': 'Blue'
      },
  ]

CKEDITOR_5_CONFIGS = { 
  'default': {
      'toolbar': ['heading', '|', 'bold', 'italic', 'link',
                  'bulletedList', 'numberedList', 'blockQuote', 'imageUpload', ],

  },
  'extends': {
      'blockToolbar': [
          'paragraph', 'heading1', 'heading2', 'heading3',
          '|',
          'bulletedList', 'numberedList',
          '|',
          'blockQuote',
      ],
      'toolbar': ['heading', '|', 'outdent', 'indent', '|', 'bold', 'italic', 'link', 'underline', 'strikethrough',
      'code','subscript', 'superscript', 'highlight', '|', 'codeBlock', 'sourceEditing', 'insertImage',
                  'bulletedList', 'numberedList', 'todoList', '|',  'blockQuote', 'imageUpload', '|',
                  'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', 'mediaEmbed', 'removeFormat',
                  'insertTable',],
      'image': {
          'toolbar': ['imageTextAlternative', '|', 'imageStyle:alignLeft',
                      'imageStyle:alignRight', 'imageStyle:alignCenter', 'imageStyle:side',  '|'],
          'styles': [
              'full',
              'side',
              'alignLeft',
              'alignRight',
              'alignCenter',
          ]

      },
      'table': {
          'contentToolbar': [ 'tableColumn', 'tableRow', 'mergeTableCells',
          'tableProperties', 'tableCellProperties' ],
          'tableProperties': {
              'borderColors': customColorPalette,
              'backgroundColors': customColorPalette
          },
          'tableCellProperties': {
              'borderColors': customColorPalette,
              'backgroundColors': customColorPalette
          }
      },
      'heading' : {
          'options': [
              { 'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph' },
              { 'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1' },
              { 'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2' },
              { 'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3' }
          ]
      }
  },
  'list': {
      'properties': {
          'styles': 'true',
          'startIndex': 'true',
          'reversed': 'true',
      }
  }

}


ASGI_APPLICATION = 'bigBallz.asgi.application'

CHANNEL_LAYERS = {
    'default': {
    'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
        "hosts": [('127.0.0.1', 6379)],
        },
    },
}

# settings.py
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

ROOT_URLCONF = 'bigBallz.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
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

STATICFILES_DIRS = [
    os.path.join(BASE_DIR,'authentication/static/')
]
STATIC_ROOT = os.path.join(BASE_DIR,'static')
MEDIA_ROOT = os.path.join(BASE_DIR,'media')

WSGI_APPLICATION = 'bigBallz.wsgi.application'

LOGIN_URL = '/signin'
LOGOUT_REDIRECT_URL = '/sample'
STATIC_URL = '/static/'
MEDIA_URL = '/media/'




# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases


DATABASES = {
    'default' : {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME' : config('DATA_BASE'),
        'USER' : config('USER'),
        'PASSWORD' : config('PASSWORD'),
        'HOST' : config('HOST'),
        'PORT' : config('PORT')

    }
    
}

"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR,'db.sqlite3'),
    }
}
"""

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Los_Angeles'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

try:
    from .local_settings import *
except ImportError:
    pass

