import os
import sys
sys.path.append('..')

from .local import *


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INSTALLED_APPS = [
	'tests',
	'prov_vo',
	'vosi',
	'rest_framework',
	'django.contrib.auth',
	'django.contrib.contenttypes',
]
SECRET_KEY = 'This is a secret key for testing'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME':  os.path.join(BASE_DIR, 'provdb.sqlite3'),
    }
}
ROOT_URLCONF = 'tests.urls'

# custom settings for prov_vo app:
# PROV_VO_CONFIG = {
#     'namespaces': {
#         'rave': "http://www.rave-survey.org/prov/",
#     },
#     'provdalform': {
#         'obj_id.help_text': "Please enter the identifier for an entity (e.g. rave:20030411_1507m23_001 or rave:20121220_0752m38_089) or an activity (e.g. rave:act_irafReduction)"
#     }
# }
