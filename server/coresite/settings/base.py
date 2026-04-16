from .environment import env, os, BASE_DIR
from .application import (
    DJANGO_APPLICATIONS,
    CUSTOM_APPLICATIONS,
    THIRD_PARTY_APPLICATIONS,
)

SETTINGS_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

SECRET_KEY = env("SECRET_KEY")

DEBUG = True

ALLOWED_HOSTS = ["*"]
DOMAIN = env("DOMAIN")
RESET_PASSWORD_URL = env("RESET_PASSWORD_URL")

ROOT_URLCONF = 'coresite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(SETTINGS_PATH, 'templates')],
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

INSTALLED_APPS = [
    *DJANGO_APPLICATIONS,
    *CUSTOM_APPLICATIONS,
    *THIRD_PARTY_APPLICATIONS,
]

WSGI_APPLICATION = 'coresite.wsgi.application'

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Karachi'

USE_I18N = True

USE_TZ = True
COMPANY_NAME = env("COMPANY_NAME")
COMPANY_COPYRIGHT = env("COMPANY_COPYRIGHT")
COMPANY_ADDRESS = env("COMPANY_ADDRESS")
COMPANY_EMAIL = env("COMPANY_EMAIL")
COMPANY_PHONE = env("COMPANY_PHONE")
COMPANY_WEBSITE = env("COMPANY_WEBSITE")
COMPANY_LOGO = env("COMPANY_LOGO")
COMPANY_LOGO_TEXT = env("COMPANY_LOGO_TEXT")
PRIMARY_COLOR = env("PRIMARY_COLOR")
SECONDARY_COLOR = env("SECONDARY_COLOR")
BUTTON_COLOR = env("BUTTON_COLOR")
TEXT_COLOR = env("TEXT_COLOR")
STARTING_YEAR = env("COMPANY_STARTING_YEAR")
FROM_EMAIL = env("EMAIL_FROM")
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
REACT_DOMAIN = env("REACT_DOMAIN")

SPECTACULAR_SETTINGS = {
    'TITLE': 'ERP Backend API',
    'DESCRIPTION': 'REST API for user authentication and profile management.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
}
