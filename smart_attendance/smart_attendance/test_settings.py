import os
from .settings import *

# Override database for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable email for testing
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'