"""
Django settings for discuss project.
"""

import os
import sentry_sdk
from pathlib import Path
from sentry_sdk.integrations.django import DjangoIntegration

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-5asdj4^2_uy(k6)6v2+_q@ij!&ld*ndf3-_z$wr9zqcr2$1p&1'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['0.0.0.0', 'localhost', '127.0.0.1', '.replit.dev', '.repl.co']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sites',  # Required for django-allauth
    
    # Installed apps
    'core',
    'user_guide',
    
    # Third-party packages
    'rest_framework',
    'markdownx',
    'debug_toolbar',
    'django_filters',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'el_pagination',
    # 'cacheops',  # Temporarily disabled due to compatibility issues
    # 'avatar',    # Replaced with native ImageField in Profile model
    'taggit',    # For adding tags to profiles and content
    'django_countries',  # For country selection in profiles
    'mptt',      # For improved hierarchical comment trees
    'watson',    # For advanced full-text search
    'payments',   # For processing payments and donations
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'allauth.account.middleware.AccountMiddleware',  # Required by django-allauth
]

# Debug Toolbar
INTERNAL_IPS = ['127.0.0.1', '0.0.0.0']

# CSRF Settings for Replit
CSRF_TRUSTED_ORIGINS = [
    'https://*.replit.dev',  # Trust all Replit domains
    'https://*.replit.app',
    'http://localhost:5000',
    'http://127.0.0.1:5000',
]

ROOT_URLCONF = 'discuss.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
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

WSGI_APPLICATION = 'discuss.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

import os
import dj_database_url

# Use DATABASE_URL environment variable if available, otherwise fall back to SQLite
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Media files (User uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login URLs
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
}

# Markdownx settings
MARKDOWNX_UPLOAD_MAX_SIZE = 5 * 1024 * 1024  # 5MB
MARKDOWNX_MEDIA_PATH = 'markdownx/'

# Search settings will be configured later

# django-allauth configuration
SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',
    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Allauth settings
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']
ACCOUNT_LOGIN_METHODS = {'username', 'email'}

# django-notifications-hq settings
DJANGO_NOTIFICATIONS_CONFIG = {
    'USE_JSONFIELD': True,
}

# django-el-pagination settings
EL_PAGINATION_PER_PAGE = 10
EL_PAGINATION_PAGE_OUT_OF_RANGE_404 = True

# django-cacheops settings
CACHEOPS_REDIS = {
    'host': 'localhost',
    'port': 6379,
    'db': 1,
}

CACHEOPS_DEFAULTS = {
    'timeout': 60*60  # 1 hour cache timeout
}

CACHEOPS = {
    # Cache all queries in core app for 1 hour
    'core.*': {'ops': 'all', 'timeout': 60*60},
    # Cache specific models for different durations
    'auth.user': {'ops': {'fetch', 'get'}, 'timeout': 60*60},
    'auth.*': {'ops': ('fetch', 'get'), 'timeout': 60*60},
    '*.*': {'ops': (), 'timeout': 60*60},  # Disable caching for all other models
}

# Custom Avatar settings (replaced django-avatar with direct ImageField)
# Avatar images are now stored in the MEDIA_ROOT/avatars directory
# and managed directly through the Profile model

# Django Taggit settings
TAGGIT_CASE_INSENSITIVE = True

# Django Countries settings
COUNTRIES_FLAG_URL = 'https://flagicons.lipis.dev/flags/4x3/{code}.svg'

# Django Payments settings
PAYMENT_HOST = '0.0.0.0:5000'
PAYMENT_USES_SSL = False
PAYMENT_MODEL = 'core.Payment'
PAYMENT_VARIANTS = {
    'default': ('payments.dummy.DummyProvider', {}),
    'paypal': ('payments.paypal.PaypalProvider', {
        'client_id': '',
        'secret': '',
        'endpoint': 'https://api.sandbox.paypal.com',
        'capture': True,
    }),
    'stripe': ('payments.stripe.StripeProvider', {
        'secret_key': '',
        'public_key': '',
    })
}

# Sentry configuration for error tracking
SENTRY_DSN = os.environ.get('SENTRY_DSN', '')
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
        ],
        
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        traces_sample_rate=0.5,
        
        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True,
        
        # By default the SDK will try to use the SENTRY_RELEASE
        # environment variable, or infer a git commit
        # SHA as release, however you may want to set
        # something more human-readable.
        # release="discuss@1.0.0",
        
        # How many seconds to wait before sending the event to Sentry
        shutdown_timeout=2.0,
        
        # Set environment name 
        environment="development" if DEBUG else "production",
    )
