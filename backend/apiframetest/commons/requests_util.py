"""
@ Title:
@ Author: Cathy
@ Time: 2025/3/3 11:25
"""
import logging

import allure
import requests

logger = logging.getLogger(__name__)

class RequestsUtil:
    sess = requests.session()
    def send_all_requests(self, **kwargs):
        logger.info(f"请求的数据为：{kwargs}")
        # 添加 Allure 请求日志
        with allure.step("API Request"):
            allure.attach(
                str(kwargs),
                name="Request Details",
                attachment_type=allure.attachment_type.JSON
            )

        res = RequestsUtil.sess.request(**kwargs)
        logger.info(f"响应的数据为：{res.json()}")
        # 添加 Allure 响应日志
        with allure.step("API Response"):
            allure.attach(
                str(res.status_code),
                name="Status Code",
                attachment_type=allure.attachment_type.TEXT
            )
            allure.attach(
                str(res.headers),
                name="Response Headers",
                attachment_type=allure.attachment_type.JSON
            )
            allure.attach(
                str(res.json()) if res.content else "{}",
                name="Response Body",
                attachment_type=allure.attachment_type.JSON
            )

        return res