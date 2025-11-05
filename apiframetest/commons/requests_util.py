"""
@ Title:
@ Author: Cathy
@ Time: 2025/3/3 11:25
"""
import requests
from apiframetest.commons.log_util import logger

class RequestsUtil:
    sess = requests.session()
    def send_all_requests(self, **kwargs):
        logger.info(f"请求的数据为：{kwargs}")
        print(f">>>请求的数据为：{kwargs}")
        res = RequestsUtil.sess.request(**kwargs)
        logger.info(f"响应的数据为：{res.json()}")
        print(f">>>响应的数据为：{res.json()}")
        return res