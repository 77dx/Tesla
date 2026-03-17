"""
[DEPRECATED] apiframetest.commons.main_util
此模块已废弃，请使用 case_api.engine.CaseRunner 替代。
保留仅供参考，请勿在新功能中使用。
"""
# [DEPRECATED] 2026-03-12: 新版执行引擎已移至 case_api/engine.py
#   - CaseRunner   替代本模块的 MainUtil.stand_case_flow

import logging

from Tesla import settings
from apiframetest.commons.extract_util import ExtractUtil
# from apiframetest.commons.log_util import logger
from apiframetest.commons.requests_util import RequestsUtil
from apiframetest.commons.assert_util import AssertUtil
from apiframetest.configs import setting

logger = logging.getLogger(__name__)
class MainUtil:

    def stand_case_flow(self, case_obj):
        logger.info(f"模块>功能>用例名称：{case_obj.feature}>{case_obj.story}>{case_obj.title}")
        # 从extract.yaml中提取并替换数据
        new_request = ExtractUtil().change(case_obj.request)
        # 请求接口
        res = RequestsUtil().send_all_requests(**new_request)

        # 从响应中提取数据,保存进extract.yaml文件中
        try:
            if case_obj.extract:
                for k, v in case_obj.extract.items():
                    ExtractUtil().extract_key(setting.extract_path, res, k, *v)
        except Exception as e:
            logger.error(f'数据提取失败: {e}')

        # 断言部分
        try:
            validate = case_obj.validate
            if validate:
                for assert_type, assert_data in ExtractUtil().change(validate).items():
                    AssertUtil().assert_all_case(res, assert_type, assert_data)
                    logger.info("断言成功 \n")
            else:
                logger.error("此用例没有断言 \n")
        except Exception as e:
            logger.error(f"断言失败：{e} \n")
