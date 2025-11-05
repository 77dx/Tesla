"""
@ Title:
@ Author: Cathy
@ Time: 2025/5/22 16:33
"""
from copy import deepcopy

from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response


class CodeResultMessageRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response: Response = renderer_context.get("response")

        # 所用的前端框架naive-admin所设定的格式
        response_dict = {
            "code": response.status_code,
            "message": "ok",
            "result": data
        }
        if 300 >= response.status_code >= 200:
            response_dict['code'] = 200
        elif response.status_code >= 400:
            if 'detail' in data:
                response_dict['message'] = data['detail']
            elif 'msg' in data:
                response_dict['message'] = data['msg']
            elif isinstance(data, dict):
                msg = list(data.values())[0]
                response_dict['message'] = msg
            elif isinstance(data, list):
                msg = str(data[0])
                response_dict['message'] = msg
        return super().render(response_dict, accepted_media_type, renderer_context)
