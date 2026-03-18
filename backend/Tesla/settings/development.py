"""
开发环境配置

启动方式：
  DJANGO_SETTINGS_MODULE=Tesla.settings.development python manage.py runserver
  或直接在 manage.py / wsgi.py 中指定（见各文件）
"""
from .base import *  # noqa

DEBUG = True
ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
