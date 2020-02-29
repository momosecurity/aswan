"""
Settings for production

SECURITY WARNING: Please change to your product environment specific settings
"""

from project.settings.base import *


#################
# Project basic #
#################
DEBUG = False
SECRET_KEY = '=====PLEASE_REPLACE_THIS_SECRET_KEY_IN_PRODUCTION_MODE====='

ALLOWED_HOSTS = [
    "*",
]


######################
# Databases settings #
######################
DATABASES = {
    'default': {
        "ENGINE": 'django.db.backends.mysql',
        "HOST": "127.0.0.1",
        "PORT": 3306,
        "USER": "root",
        "PASSWORD": "root",
        "DATABASE_CHARSET": "utf8",
        "NAME": "risk_control",
    },
}
