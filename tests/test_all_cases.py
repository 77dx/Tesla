"""
@ Title:
@ Author: Cathy
@ Time: 2025/3/3 15:02
"""
import logging

import allure
import pytest
from pathlib import Path
from apiframetest.commons.main_util import MainUtil
from apiframetest.commons import yaml_util, ddt_util
from apiframetest.commons.model_util import verify_yaml

logger = logging.getLogger(__name__)


@allure.epic("鱼小七测试平台")
class TestAllCases:
    pass

def create_testcase(yaml_file):
    @pytest.mark.parametrize("caseinfo", ddt_util.read(yaml_file))
    def func(self, caseinfo):
        global case_obj
        # 如果是列表，就需要循环
        if isinstance(caseinfo, list):
            for case in caseinfo:
                # 对yaml文件的用例进行关键字校验
                case_obj = verify_yaml(case, yaml_file.name)
                MainUtil().stand_case_flow(case_obj)
        else:  # 不是列表就是单用例
            # 对yaml文件的用例进行关键字校验
            case_obj = verify_yaml(caseinfo,yaml_file.name)
            MainUtil().stand_case_flow(case_obj)

        allure.dynamic.feature(case_obj.feature)
        allure.dynamic.story(case_obj.story)
        allure.dynamic.title(case_obj.title)
    return func

# 执行tests中所有的yaml文件
tests = Path(__file__).parent
test_case_yaml = tests / "test_case_yaml"
yaml_files= list(test_case_yaml.glob("**/*.yaml"))
logger.info(f"收集到的yaml文件：{list(yaml_files)}")
for yaml_file in yaml_files:
    method_name = f'test_{yaml_file.stem}_{hash(yaml_file)}'
    logger.info(f"生成的用例名称：{method_name}")
    # 如果测试用例名称重复就抛出异常
    if hasattr(TestAllCases, method_name):
        raise ValueError(f"重复的测试方法名：{method_name}")
    setattr(TestAllCases, method_name, create_testcase(yaml_file))


