"""
Django settings for beatsight project.

Generated by 'django-admin startproject' using Django 4.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os
import sys
import re
from pathlib import Path
import time

from django.templatetags.static import static
import grpc

import license_pb2
import license_pb2_grpc


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-st%(1*!&8_beuku+flr30t$(gdyt+^!e5xzaz)536jf(rb^rnq'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",  # optional, if special filters are needed
    "unfold.contrib.forms",  # optional, if special form elements are needed
    "unfold.contrib.inlines",  # optional, if special inlines are needed    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # "corsheaders",
    'rest_framework',
    'django_celery_beat',
    'django_celery_results',
    'compressor',

    'core.apps.CoreConfig',
    'projects.apps.ProjectsConfig',
    'repo_sync.apps.RepoSyncConfig',
    'stats.apps.StatsConfig',
    'developers.apps.DevelopersConfig',
    'profiles.apps.ProfilesConfig',
]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'beatsight.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates')
        ],
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

WSGI_APPLICATION = 'beatsight.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    # {
    #     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'zh-Hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static-local')
]

COMPRESS_ENABLED = True
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        # 'rest_framework.authentication.BasicAuthentication'
    ],
    'DEFAULT_PAGINATION_CLASS': 'beatsight.pagination.CustomPagination',
    'EXCEPTION_HANDLER': 'beatsight.views.custom_exception_handler',
    'PAGE_SIZE': 10,
}

# Celery settings
CELERY_BROKER_URL = "amqp://guest:guest@rabbitmq:5672"
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:4200',
]
# CORS_ORIGIN_WHITELIST = [
#     'http://localhost:4200',
# ]
# CORS_ALLOWED_ORIGINS = ['http://localhost:4200']

# ###### custsom settings
SERVER_VERSION = '1.2.0'
CORE_SERVICE = 'localhost:50051'

LOGIN_REDIRECT_URL = '/dashboard'

ALLOWED_HOSTS = [
    '*',
]

BEATSIGHT_DATA_DIR = '/beatsight-data'

UNFOLD = {
    "SITE_TITLE": 'BeatSight 管理后台',
    "SITE_HEADER": 'BeatSight 管理后台',
    "SITE_FAVICONS": [
        {
            "rel": "icon",
            "sizes": "32x32",
            "type": "image/png",
            "href": lambda request: static("assets/img/favicon.ico"),
        },
    ],
    "SITE_LOGO": {
        "light": lambda request: static("assets/img/logo.jpg"),  # light mode
        "dark": lambda request: static("assets/img/logo-dark.jpg"),  # dark mode
    },
    "SIDEBAR": {
        "show_search": True,  # Search in applications and models names
        "show_all_applications": True,  # Dropdown with all applications and models
    },
}


LOGNAME = 'beatsight'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s %(pathname)s:%(lineno)d: %(levelname)-5s: %(funcName)s()- %(message)s'
        },
        'simple': {
            'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)s %(funcName)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
        'beatsight_log_hdlr': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(str(BASE_DIR) + '/logs/', 'beatsight.log'),
            'maxBytes': 1024 * 1024 * 500,  # 500 MB
            'backupCount': 10,
            'formatter': 'standard',
        },
        'beatsight_task_log_hdlr': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(str(BASE_DIR) + '/logs/', 'task.log'),
            'maxBytes': 1024 * 1024 * 500,  # 500 MB
            'backupCount': 10,
            'formatter': 'standard',
        },
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'scprits_handler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(str(BASE_DIR) + '/logs/', 'script.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'standard',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True
        },
        'beatsight': {
            'handlers': [
                'console', 'beatsight_log_hdlr',
            ],
            'level': 'DEBUG',
            'propagate': True
        },
        'django.request': {
            'handlers': [
                'mail_admins', 'beatsight_log_hdlr',
            ],
            'level': 'DEBUG',
            'propagate': True
        },
        'tasks': {
            'handlers': [
                'console', 'beatsight_task_log_hdlr',
            ],
            'level': 'DEBUG',
            'propagate': True
        },
        'scripts': {
            'handlers': ['scprits_handler'],
            'level': 'ERROR',
            'propagate': False
        },
    }
}


def load_local_settings(module):
    """Import any symbols that begin with A-Z. Append to lists any symbols that begin with "EXTRA_".
    """
    for attr in dir(module):
        match = re.search('^EXTRA_(\w+)', attr)
        if match:
            name = match.group(1)
            value = getattr(module, attr)
            try:
                globals()[name] += value
            except KeyError:
                globals()[name] = value
        elif re.search('^[A-Z]', attr):
            globals()[attr] = getattr(module, attr)

try:
    from . import local_settings
    print("loading local_settings ... Done.")
except ImportError:
    pass
else:
    load_local_settings(local_settings)
    del local_settings


try:
    sys.path.append(os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../../runtime')
    ))
    import beatsight_settings
    print("loading beatsight_settings ... Done.")
except ImportError:
    pass
else:
    load_local_settings(beatsight_settings)
    del beatsight_settings

# --------------------
TMP_REPO_DATA_DIR = os.path.join(BEATSIGHT_DATA_DIR, 'temp-repos')
REPO_DATA_DIR = os.path.join(BEATSIGHT_DATA_DIR, 'repos')
STAT_DB_DIR = os.path.join(BEATSIGHT_DATA_DIR, 'stats')

if not os.path.exists(TMP_REPO_DATA_DIR):
    os.makedirs(TMP_REPO_DATA_DIR)
print(f'TMP_REPO_DATA_DIR: {TMP_REPO_DATA_DIR}')

if not os.path.exists(REPO_DATA_DIR):
    os.makedirs(REPO_DATA_DIR)
print(f'REPO_DATA_DIR: {REPO_DATA_DIR}')

if not os.path.exists(STAT_DB_DIR):
    os.makedirs(STAT_DB_DIR)

# core_service_connected = False
# cnt = 3
# while cnt > 0:
#     with grpc.insecure_channel(CORE_SERVICE) as channel:
#         stub = license_pb2_grpc.LicenseServiceStub(channel)

#         # Create a valid request
#         request = license_pb2.Empty()
#         # Call the GetLicenseData method
#         try:
#             stub.Ping(request)
#             print('Core service connected.')
#             core_service_connected = True
#             cnt = 0
#         except grpc.RpcError as e:
#             print(f"gRPC Error: {e}")
#             time.sleep(2)
#             cnt -= 1

# if core_service_connected is False:
#     raise Exception("Failed to start beatsight project.")
