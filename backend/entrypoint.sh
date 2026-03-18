#!/bin/sh
# backend/entrypoint.sh
# 容器启动入口脚本：自动执行数据库迁移、静态文件收集、权限初始化，然后启动服务

set -e

echo "[entrypoint] 等待数据库就绪..."
# 简单重试等待 DB（生产用 MySQL 时有效，SQLite 直接跳过）
if [ "$DB_HOST" != "" ]; then
  until python -c "import MySQLdb; MySQLdb.connect(host='$DB_HOST', user='$DB_USER', passwd='$DB_PASSWORD', db='$DB_NAME')" 2>/dev/null; do
    echo "[entrypoint] 数据库未就绪，3秒后重试..."
    sleep 3
  done
  echo "[entrypoint] 数据库已就绪"
fi

echo "[entrypoint] 执行数据库迁移..."
python manage.py migrate --noinput

echo "[entrypoint] 收集静态文件..."
python manage.py collectstatic --noinput

echo "[entrypoint] 初始化权限码..."
python manage.py init_permissions

echo "[entrypoint] 启动服务: $@"
exec "$@"
