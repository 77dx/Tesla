"""
Django settings - 基础配置（所有环境共用）

使用方式：
  开发环境：DJANGO_SETTINGS_MODULE=Tesla.settings.development
  生产环境：DJANGO_SETTINGS_MODULE=Tesla.settings.production
"""
from datetime import timedelta, datetime
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ==================== 测试框架配置 ====================
TEST_YAML_PATH = BASE_DIR / 'tests/test_case_yaml'
TEST_ALL_CASES = BASE_DIR / 'tests/test_all_cases.py'
EXTRACT_PATH = BASE_DIR / 'tests/extract.yaml'
REPORT_DIR = BASE_DIR / 'reports'

# ==================== 测试套件执行配置 ====================
SUITE_EXECUTION_BASE_DIR = BASE_DIR / 'upload_yaml'
MAX_CONCURRENT_SUITES = 6
PYTEST_EXECUTION_TIMEOUT = 300
ALLURE_GENERATION_TIMEOUT = 120
PYTEST_ARGS = ['-v', '--tb=short']
ALLURE_ARGS = ['--clean']

# ==================== Celery 配置 ====================
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://127.0.0.1:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', CELERY_BROKER_URL)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ENABLE_UTC = False
CELERY_TIMEZONE = 'Asia/Shanghai'

# ==================== 默认头像 ====================
DEFAULT_AVATAR_URL = '/media/avatar/wukong.jpg'

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-*i^0j2d*2j&p0zcf@^l3hunhe_4*zj4=mw(r$5pk=9k^#yrbjo')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 第三方
    'corsheaders',
    'drf_spectacular',
    'drf_spectacular_sidecar',
    'rest_framework',
    'rest_framework.authtoken',
    'django_q',
    # 业务应用
    'beifan',
    'account',
    'system',
    'project',
    'case_api',
    'case_ui',
    'suite',
    'snippet',
    'apiframetest',
    'product_line',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = 'Tesla.urls'

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

WSGI_APPLICATION = 'Tesla.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = False
APPEND_SLASH = True

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'Tesla.customPagination.CustomPageNumberPagination',
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'PAGE_SIZE': 10,
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'EXCEPTION_HANDLER': 'snippet.myexception.customer_exception_handler',
    'DEFAULT_RENDERER_CLASSES': [
        'Tesla.renderer.CodeResultMessageRenderer'
    ]
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Tesla API 文档',
    'VERSION': '1.0.2',
    'SWAGGER_UI_DIST': 'SIDECAR',
    'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
    'REDOC_DIST': 'SIDECAR',
}

# django-q 配置
Q_CLUSTER = {
    'orm': 'default',
    'timeout': 60 * 10,
    'retry': 60 * 10 * 2,
    'workers': 2,
    'bulk': 10,
}

# 日志配置
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

def _get_logfile():
    return str(LOG_DIR / f"django_{datetime.now().strftime('%Y%m%d')}.log")

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'},
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': _get_logfile(),
            'formatter': 'standard',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'loggers': {
        '': {'handlers': ['file', 'console'], 'level': 'INFO', 'propagate': True},
    },
}
