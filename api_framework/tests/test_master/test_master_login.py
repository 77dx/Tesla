"""
@ Title:
@ Author: Cathy
@ Time: 2024/12/10 17:11
"""
import pytest
import requests
import yaml
from pathlib import Path
import logging
import os
import time

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# 加载 YAML 数据
def load_test_data(file_path):
    project_path = Path(__file__).parent.parent.parent
    file_path = project_path / "case_data" / file_path
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

# 参数化测试
@pytest.mark.parametrize("test_case", load_test_data("user_login.yaml")["test_cases"])
def test_login(test_case):
    url = "http://127.0.0.1:8000/beifan/login"
    payload = {
        "username": test_case["username"],
        "password": test_case["password"]
    }
    logger.info(f"Testing with payload: {payload}")
    response = requests.post(url, json=payload)
    logger.info(f"Response: {response.status_code}, Body: {response.text}")
    assert response.status_code == test_case["expected_status"]

    # 处理log保存路径,log文件不正确
    dirname = Path(__file__).parent.name
    log_path = Path(__file__).parent.parent.parent / "logs" / dirname
    log_dir = f"{log_path}_{int(time.time())}"
    os.mkdir(log_dir)

    log_file_path = Path(log_dir) / log_dir / f"{int(time.time())}.log"
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(file_handler)


if __name__ == '__main__':
    dirname = Path(__file__).parent.name
    log_path = Path(__file__).parent.parent.parent / "logs" / dirname
    log_dir = f"{log_path}{int(time.time())}"
    os.mkdir(log_dir)
    log_file_path = Path(log_dir) / log_path / f"{int(time.time())}.log"
    print(log_file_path)


