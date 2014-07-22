# coding=utf-8

"""Local Settings for the Django Short Urls application"""

from __future__ import unicode_literals

DEBUG = True

ADMINS = (
    ('User Name', 'username@work4labs.com'),
)

SERVER_EMAIL = "root@work4labs.com"

MONGOENGINE = {
    'db': 'work4labs',
    'host': 'localhost',
    'port': 27017,
    'username': 'work4labs',
    'password': 'work4labs'
}

ALLOWED_HOSTS = ['.workfor.us']

# Make this unique, and don't share it with anybody.
SECRET_KEY = '6r__q4gindk5hzbb^)u!q%4-!d&amp;clxu#%0g3v4m@rg7!xf$#=@'

SENTRY_DSN = None

# Do *not* set to True if you're connecting to the production database!
MONGO_AUTO_CREATE_INDEXES = True
