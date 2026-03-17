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

        # 204 No Content：删除成功等无响应体的情况，直接返回空 bytes，不写 body
        if response.status_code == 204 or data is None:
            return b''

        # 所用的前端框架naive-admin所设定的格式
        response_dict = {
            "code": response.status_code,
            "message": "ok",
            "result": data
        }
        if 300 >= response.status_code >= 200:
            response_dict['code'] = 200
        elif response.status_code >= 400:
            if isinstance(data, dict):
                if 'detail' in data:
                    response_dict['message'] = data['detail']
                elif 'msg' in data:
                    response_dict['message'] = data['msg']
                else:
                    msg = list(data.values())[0]
                    response_dict['message'] = str(msg[0]) if isinstance(msg, list) else str(msg)
            elif isinstance(data, list) and data:
                response_dict['message'] = str(data[0])
        return super().render(response_dict, accepted_media_type, renderer_context)
