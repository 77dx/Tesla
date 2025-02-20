"""
@ Title:
@ Author: Cathy
@ Time: 2024/12/17 15:01
"""
from rest_framework.views import exception_handler

def customer_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        response.data.clear()
        response.data['code'] = response.status_code
        if response.status_code == 405:
            response.data['msg'] = "请求不允许"
        elif response.status_code == 401:
            response.data['msg'] = "认证未通过"
        elif response.status_code == 403:
            response.data['msg'] = "禁止访问"
        elif response.status_code == 404:
            response.data['msg'] = "未找到文件"
        elif response.status_code >= 500:
            response.data['msg'] = "服务器异常"
        else:
            response.data['msg'] = "其他未知错误"
        response.data['data'] = []
    return response
