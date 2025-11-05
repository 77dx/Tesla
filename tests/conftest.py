"""
@ Title:
@ Author: Cathy
@ Time: 2025/5/9 15:10
# """
import pytest

from apiframetest.commons import yaml_util
from apiframetest.configs import setting
from Tesla import settings

# 在执行用例前清除extract.yaml中的中间变量的值
@pytest.fixture(scope="session", autouse=True)
def clear_extract():
    yaml_util.clean(setting.extract_path)

# 用于调试，清除旧yaml文件
# @pytest.fixture(scope="session", autouse=True)
# def clear_case_yaml():
#     yaml_util.clear_folder(settings.TEST_YAML_PATH)




