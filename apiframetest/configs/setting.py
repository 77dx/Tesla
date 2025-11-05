"""
@ Title:
@ Author: Cathy
@ Time: 2025/3/10 16:58
"""
from pathlib import Path

# 当前的环境配置   release，test, dev
current_env = "release"

# 数据库配置
db_config = {
    "user": "root",
    "password": "Dx396321556",
    "host": "127.0.0.1",
    "port": 3306,
    "database":"apiframe"
}

# 存储中间变量的文件
base_dir = Path(__file__).resolve().parent.parent
extract_path = base_dir / "extract.yaml"
