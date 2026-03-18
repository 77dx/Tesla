"""
生产环境配置

所有敏感配置通过环境变量注入，不硬编码在代码中。

必填环境变量：
  DJANGO_SECRET_KEY   Django 密钥
  DB_NAME             数据库名
  DB_USER             数据库用户
  DB_PASSWORD         数据库密码
  DB_HOST             数据库主机
  CELERY_BROKER_URL   Redis 地址（如 redis://redis:6379/0）

可选环境变量：
  DB_PORT             数据库端口（默认 5432）
  ALLOWED_HOSTS       允许的域名，逗号分隔（默认 *）
"""
import os
from .base import *  # noqa

DEBUG = False

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')

# 生产环境必须使用强密钥
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

# 生产数据库（MySQL）
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', 'tesla'),
        'USER': os.getenv('DB_USER', 'tesla'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# 生产环境安全设置
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# 静态文件（由 collectstatic 收集，nginx 直接服务）
STATIC_ROOT = BASE_DIR / 'staticfiles'
