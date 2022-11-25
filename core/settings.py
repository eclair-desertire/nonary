import os
from pathlib import Path
import environ
from firebase_admin import initialize_app

FIREBASE_APP = initialize_app()

env = environ.Env()
environ.Env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('DJANGO_SECRET')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

# Application definition

DEFAULT_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'corsheaders',
    'drf_yasg',
    'django_cleanup.apps.CleanupConfig',
    'django_extensions',
    'after_response',
    'rest_framework.authtoken',
    'fcm_django',
    'channels',
    'django_filters',
    'django_db_logger',
    'django_summernote',
]

LOCAL_APPS = [
    'utils',
    'auth_user.apps.AuthUserConfig',
    'location.apps.LocationConfig',
    'main_page.apps.MainPageConfig',
    'shop.apps.ShopConfig',
    'chat.apps.ChatConfig',
    'promo.apps.PromoConfig',
    'notification.apps.NotificationConfig',
    'contact.apps.ContactConfig',
    'app_filter.apps.AppFilterConfig',
    'order.apps.OrderConfig',
    'external.apps.ExternalConfig',
]

INSTALLED_APPS = DEFAULT_APPS + THIRD_PARTY_APPS + LOCAL_APPS

if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']

AUTH_USER_MODEL = 'auth_user.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# if DEBUG:
#     MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

ROOT_URLCONF = 'core.urls'

FCM_DJANGO_SETTINGS = {
    # an instance of firebase_admin.App to be used as default for all fcm-django requests
    # default: None (the default Firebase app)
    "DEFAULT_FIREBASE_APP": None,
    # default: _('FCM Django')
    "APP_VERBOSE_NAME": "tvoy.kz",
    # true if you want to have only one active device per registered user at a time
    # default: False
    "ONE_DEVICE_PER_USER": True,
    # devices to which notifications cannot be sent,
    # are deleted upon receiving error response from FCM
    # default: False
    "DELETE_INACTIVE_DEVICES": False,
    # Transform create of an existing Device (based on registration id) into
    # an update. See the section
    # "Update of device with duplicate registration ID" for more details.
    "UPDATE_ON_DUPLICATE_REG_ID": True,
}

GOOGLE_APPLICATION_CREDENTIALS = env('GOOGLE_APPLICATION_CREDENTIALS')

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

WSGI_APPLICATION = 'core.wsgi.application'
ASGI_APPLICATION = "core.asgi.application"

DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda request: False  # DEBUG,
}

SWAGGER_SETTINGS = {
    'LOGOUT_URL': '/admin/logout/',
    'LOGIN_URL': '/admin/login/',
    'DEFAULT_MODEL_RENDERING': 'example',
    'SECURITY_DEFINITIONS': {
        'Basic': {
            'type': 'basic'
        },
        'DRF Token': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    }
}

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env('POSTGRES_DB'),
        'USER': env('POSTGRES_USER'),
        'PASSWORD': env('POSTGRES_PASSWORD'),
        'HOST': env('POSTGRES_HOST'),
        'PORT': env('POSTGRES_PORT')
    }
}

# Password validation
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

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.AllowAny',),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'utils.pagination.FasterPageNumberPagination',
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    'DEFAULT_METADATA_CLASS': 'rest_framework_json_api.metadata.JSONAPIMetadata',
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'PAGE_SIZE': 25
}

# Internationalization

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'Asia/Almaty'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = env('STATIC_ROOT')
MEDIA_URL = 'media/'
MEDIA_ROOT = env('MEDIA_ROOT')
STATICFILES_DIRS = (
    'static',
)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS')

CURRENT_SITE = env('CURRENT_SITE')
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env('EMAIL_PORT')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True

SMS_LOGIN = env('SMS_LOGIN')
SMS_PASS = env('SMS_PASS')
IS_SEND_SMS = env.bool('IS_SEND_SMS')
TOKEN_LIFETIME_IN_MINUTES = int(env('TOKEN_LIFETIME_IN_MINUTES'))
IS_VERIFY_EMAIL = env.bool('IS_VERIFY_EMAIL')
JUST_INACTIVE = env.bool('JUST_INACTIVE')
PAYMENT_URL = env('PAYMENT_URL')
CARD_TOKEN_URL = env('CARD_TOKEN_URL')
ORDER_ID_DIGITS = env.int('ORDER_ID_DIGITS')

# channels settings
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [env("REDIS_CHANNELS_URL")],
        },
    },
}

DATA_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 2048  # 2GB
FILE_UPLOAD_MAX_MEMORY_SIZE = DATA_UPLOAD_MAX_MEMORY_SIZE
YANDEX_MAP_API_KEY = env('YANDEX_MAP_API_KEY')
MERCHANT_TOKEN = env('MERCHANT_TOKEN')
MERCHANT_ORDER = env('MERCHANT_ORDER')

WEBKASSA_API = env('WEBKASSA_API')
WEBKASSA_URL = env('WEBKASSA_URL')
WEBKASSA_USERNAME = env('WEBKASSA_USERNAME')
WEBKASSA_PASSWORD = env('WEBKASSA_PASSWORD')
WEBKASSA_ID = env('WEBKASSA_ID')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s %(message)s'
        },
    },
    'handlers': {
        'db_log': {
            'level': 'DEBUG',
            'class': 'django_db_logger.db_log_handler.DatabaseLogHandler'
        },
    },
    'loggers': {
        'db': {
            'handlers': ['db_log'],
            'level': 'DEBUG'
        },
        'django.request': {  # logging 500 errors to database
            'handlers': ['db_log'],
            'level': 'ERROR',
            'propagate': False,
        }
    }
}


JAZZMIN_SETTINGS = {
    "custom_links": {
        "app_filter": [{
            "name": "Чат",
            "url": "open_chat",
            "icon": "fas fa-comments",
            "permissions": ["books.view_book"]
        }]
    },
}


def my_custom_upload_to_func():
    pass


SUMMERNOTE_THEME = 'bs4'


SUMMERNOTE_CONFIG = {
    # You can put custom Summernote settings
    'summernote': {
        # As an example, using Summernote Air-mode
        'airMode': False,

        # Change editor size
        'width': '100%',
        'height': '480',

        # Use proper language setting automatically (default)
        'lang': 'ru-RU',

        # Toolbar customization
        # https://summernote.org/deep-dive/#custom-toolbar-popover
        'toolbar': [
            ['style', ['style']],
            # ['misc', ['emoji']],
            ['font', ['bold', 'underline', 'clear']],
            ['fontname', ['fontname']],
            ['color', ['color']],
            ['para', ['ul', 'ol', 'paragraph']],
            # ['table', ['table']],
            ['insert', ['link', ]],
            ['view', ['fullscreen', 'codeview', 'help']],
        ],

    },



    # You can completely disable the attachment feature.
    'disable_attachment': False,

    # Lazy initialization
    # If you want to initialize summernote at the bottom of page, set this as True
    # and call `initSummernote()` on your page.
    'lazy': True,

    'js': (
        f'/{STATIC_URL}js/summernote-emoji.js',
    ),
    'js_for_inplace': (
        f'/{STATIC_URL}js/summernote-emoji.js',
    ),
}
