"""
@ Title:
@ Author: Cathy
@ Time: 2024/11/18 13:36
"""
from api_framework.commons.yaml_util import clean_yaml
import pytest

# 在用例执行之前清空中间参数
@pytest.fixture(scope="session", autouse=True)
def clean_extract():
    clean_yaml("extract.yaml")
