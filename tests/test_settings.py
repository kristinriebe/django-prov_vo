import os
import sys
sys.path.append('.')
#sys.path.append('..')
#from .local import *

from local import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


INSTALLED_APPS = [
	'tests',
	'prov_vo',
	'vosi',
	'rest_framework',
	'django.contrib.auth',
	'django.contrib.contenttypes',
    'django.contrib.staticfiles',
]

SECRET_KEY = 'This is a secret key for testing'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME':  os.path.join(BASE_DIR, 'testdb.sqlite3'),
    }
}
ROOT_URLCONF = 'tests.urls'

# some custom settings for prov_vo app:
PROV_VO_CONFIG = {
    'namespaces': {
        'rave': "http://www.rave-survey.org/prov/",
    },
    'provdalform': {
        'obj_id.help_text': "Please enter the identifier for an entity (e.g. rave:dr4), an activity or agent"
    }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

STATIC_URL = '/static/'
