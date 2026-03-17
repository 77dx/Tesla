"""
@ Title:
@ Author: Cathy
@ Time: 2025/3/3 15:03
"""
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class CaseInfo:
    # 必填
    feature: str
    story: str
    title: str
    request: dict
    validate: dict
    # 选填
    parametrize: list=None
    extract: dict=None


# 校验yaml文件的必填字段
def verify_yaml(caseinfo: dict, yaml_name):
    try:
        new_caseinfo = CaseInfo(**caseinfo)
        logger.info(f"{yaml_name}: 测试用例规范校验通过")
        return new_caseinfo
    except Exception as e:
        logger.error(f"{yaml_name}: 测试用例不符合规范{e}")
        raise Exception(f"{yaml_name}: 测试用例不符合规范{e}")


if __name__ == '__main__':
    caseinfo = {
        "feature": "用户模块",
        "story": "用户信息",
        "title": "检查用户信息",
        "request":{
            "url": "https://user-site-api.wanshifu.com/topMenu/getUserInfo",
            "method": "get"
        },
        "validate": None
    }
    print(verify_yaml(caseinfo))

