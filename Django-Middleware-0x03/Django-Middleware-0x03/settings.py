from datetime import timedelta
from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-pq_d^gqs_k$5qww^qh=$&meag-tpn8m*4f6mleyb#l65zlk&-p'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

AUTH_USER_MODEL = 'chats.User'

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # installed apps
    'rest_framework',
    'chats', 
    'django_filters',
    'rest_framework.authtoken',
    'rest_framework_simplejwt.token_blacklist',  # Add this for JWT token blacklisting

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware', # middleware
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 1. Request Logging: Needs user to be authenticated, so after AuthenticationMiddleware
    'messaging_app.chats.middleware.RequestLoggingMiddleware',
    
    # 2. Time Restriction: Can be relatively early, before complex view logic
    #    Does not strictly depend on authenticated user, but works fine here.
    'messaging_app.chats.middleware.RestrictAccessByTimeMiddleware',
    
    # 3. Offensive Language (Rate Limiting):
    #    Applied to POST requests, needs to run before the view processes the message.
    'messaging_app.chats.middleware.OffensiveLanguageMiddleware',
    
    # 4. Role Permission: Needs user to be authenticated and roles checked,
    #    so it must be after AuthenticationMiddleware.
    'messaging_app.chats.middleware.RolePermissionMiddleware',
]

ROOT_URLCONF = 'messaging_app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'messaging_app.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    # default pagination class 
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination', 
    'PAGE_SIZE': 20,
    # default filter backend 
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY, # Use your Django SECRET_KEY
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id', # Or 'user_id' if your custom user model uses it
    'USER_ID_CLAIM': 'user_id', # Or 'user_id' if your custom user model uses it

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),

    # This is where you point to your custom serializer if you created one
    'TOKEN_OBTAIN_SERIALIZER': 'messaging_app.chats.auth.CustomTokenObtainPairSerializer',
    # 'TOKEN_REFRESH_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenRefreshSerializer',
    # 'TOKEN_VERIFY_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenVerifySerializer',
    # 'TOKEN_BLACKLIST_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenBlacklistSerializer',
    # 'TOKEN_SLIDING_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer',
    # 'TOKEN_SLIDING_REFRESH_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer',
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False, # Keep existing loggers intact

    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'request_logger': { # Custom formatter for your request logger
            'format': '{message}', # Only the message provided by your middleware
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': { # Handler to write logs to a file
            'class': 'logging.handlers.RotatingFileHandler', # Use RotatingFileHandler for production
            'filename': 'logs/requests.log', # Path to your log file
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,            # Keep 5 backup log files
            'formatter': 'request_logger', # Use your custom formatter
        },
        'django_file': { # Example for general Django logs
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/django.log',
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
            'formatter': 'verbose',
        }
    },
    'loggers': {
        # This logger matches the name used in your middleware (`logger = logging.getLogger(__name__)`)
        # which will resolve to 'messaging_app.chats.middleware'
        'messaging_app.chats.middleware': {
            'handlers': ['file'], # Send logs to the 'file' handler
            'level': 'INFO',     # Only log INFO level messages and above
            'propagate': False,  # Prevent logs from propagating to parent loggers (e.g., django)
        },
        'django': { # General Django logger
            'handlers': ['console', 'django_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': { # Root logger for anything not specifically configured
        'handlers': ['console'],
        'level': 'WARNING',
    },
}

