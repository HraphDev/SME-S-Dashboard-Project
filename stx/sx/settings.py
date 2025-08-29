
from pathlib import Path
import os
from decouple import config
from openai import OpenAI

OPENAI_API_KEY = config("OPENAI_API_KEY")


BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = 'django-insecure-xxfmua2y*z4-#ni=kr_hj0($63_5e3v&4gwdi*#oprar&pt(_&'

DEBUG = True

ALLOWED_HOSTS = []



INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'inventory',
    'users',
    'sx',
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

ROOT_URLCONF = 'sx.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'sx.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'vestock',
        'USER': 'root',
        'PASSWORD': '',  
        'HOST': 'localhost',
        'PORT': '3307',
    }
}




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


LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


AUTH_USER_MODEL = 'users.CustomUser'

STATIC_URL = 'static/'
STATICFILES_DIRS =[ BASE_DIR / 'static']


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'




EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # Toujours pareil
EMAIL_HOST = 'smtp.gmail.com'  # Serveur SMTP Gmail
EMAIL_PORT = 587  # Port TLS
EMAIL_USE_TLS = True  # TLS activé
EMAIL_HOST_USER = 'ultimateachrafbouhia2004@gmail.com'  # Ton adresse Gmail complète
EMAIL_HOST_PASSWORD = 'yqtmoiduwcfwmudx'  # Mot de passe ou token d’application
DEFAULT_FROM_EMAIL = 'ultimateachrafbouhia2004@gmail.com'  # Expéditeur par défaut

# Add this for debugging
EMAIL_DEBUG = True
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.mail': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')