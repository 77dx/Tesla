"""
@ Title:
@ Author: Cathy
@ Time: 2024/12/17 15:01
"""
from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError


def customer_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return response

    original_data = dict(response.data) if response.data else {}
    response.data.clear()
    response.data['code'] = response.status_code

    if response.status_code == 405:
        response.data['msg'] = "请求不允许"
    elif response.status_code == 401:
        response.data['msg'] = "认证未通过"
    elif response.status_code == 403:
        response.data['msg'] = "禁止访问"
    elif response.status_code == 404:
        response.data['msg'] = "未找到资源"
    elif response.status_code >= 500:
        response.data['msg'] = "服务器异常"
    elif isinstance(exc, ValidationError):
        # 字段级校验错误：提取第一条可读错误信息作为 msg
        first_msg = _extract_first_error(original_data)
        response.data['msg'] = first_msg
        # 同时把完整字段错误放入 data，供前端按字段显示
        response.data['data'] = original_data
        return response
    else:
        response.data['msg'] = str(exc)

    response.data['data'] = []
    return response


def _extract_first_error(data):
    """从字段错误字典中提取第一条可读错误信息"""
    if not data:
        return "请求参数有误"
    for field, errors in data.items():
        if field == 'non_field_errors':
            label = ""
        else:
            label = f"{field}: "
        if isinstance(errors, list) and errors:
            return f"{label}{errors[0]}"
        elif isinstance(errors, str):
            return f"{label}{errors}"
    return "请求参数有误"
