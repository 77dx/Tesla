"""
@ Title:
@ Author: Cathy
@ Time: 2025/3/10 16:58
"""

import os

from Tesla.settings import EXTRACT_PATH

# 当前的环境配置   release，test, dev
current_env = "release"

current_url = 'https://user-site-api.wanshifu.com'

# 数据库配置
db_config = {
    "user": "root",
    "password": "Dx396321556",
    "host": "127.0.0.1",
    "port": 3306,
    "database":"apiframe"
}

# 存储中间变量的文件
# - 默认走 Tesla.settings.EXTRACT_PATH
# - suite 并行执行时可通过环境变量覆盖,实现结果隔离
extract_path = os.getenv("APIFRAME_EXTRACT_PATH", str(EXTRACT_PATH))

