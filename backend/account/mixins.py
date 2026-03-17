"""
@ Title:
@ Author: Cathy
@ Time: 2025/4/24 13:02
"""
from rest_framework.response import Response
from rest_framework import status


class EnforceContentTypeMixin:
    """
    限制请求 Content-Type 类型
    使用时设置 expected_content_type，例如 'application/json' 或 'multipart/form-data'
    """
    expected_content_type = 'application/json'

    def dispatch(self, request, *args, **kwargs):
        if self.expected_content_type and not request.content_type.startswith(self.expected_content_type):
            return Response(
                {'error': f'Content-Type 必须为 {self.expected_content_type}'},
                status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
            )
        return super().dispatch(request, *args, **kwargs)


class AdminOnlyMixin:
    """
    限制仅管理员访问
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({'error': '仅管理员可以访问'}, status=status.HTTP_403_FORBIDDEN)
        return super().dispatch(request, *args, **kwargs)


class AutoFillUserMixin:
    """
    自动将当前登录用户设置为 serializer 的 created_by 字段
    用于 ModelViewSet 的 perform_create
    """
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ActionLogMixin:
    """
    简单的日志打印，用于调试或记录用户操作
    """
    def log_action(self, request, action_name):
        user = request.user if request.user.is_authenticated else '匿名用户'
        print(f"[日志] 用户 {user} 执行了 {action_name} 操作")

    def create(self, request, *args, **kwargs):
        self.log_action(request, "创建")
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self.log_action(request, "更新")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self.log_action(request, "删除")
        return super().destroy(request, *args, **kwargs)


class StandardResponseMixin:
    """
    统一接口返回格式
    """
    def finalize_response(self, request, response, *args, **kwargs):
        original = super().finalize_response(request, response, *args, **kwargs)
        if isinstance(original.data, dict) and original.status_code == 200:
            original.data = {
                'code': 0,
                'msg': 'success',
                'data': original.data
            }
        return original
