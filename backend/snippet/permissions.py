from rest_framework.permissions import BasePermission
from system.models import Permission


class RolePermission(BasePermission):
    """
    基于角色权限码的访问控制。

    用法：
        @action(..., permission_classes=[RolePermission('case:create')])
        def create(self, request): ...

    规则：
    - 管理员（is_staff / is_superuser）自动通过，无需配置权限。
    - 其余用户：检查其所有角色聚合的权限码中是否包含指定 code。
    """

    def __init__(self, code: str):
        self.code = code

    def __call__(self):
        """使 RolePermission('code') 可以作为类传给 permission_classes"""
        return self

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        # 管理员自动放行
        if user.is_staff or user.is_superuser:
            return True
        # 检查用户角色聚合权限码
        return Permission.objects.filter(
            roles__users=user,
            code=self.code
        ).exists()


def make_permission(code: str):
    """
    工厂函数：生成一个可直接放入 permission_classes 的权限类。

    用法：
        permission_classes = [make_permission('case:delete')]
    """
    class _Perm(BasePermission):
        _code = code

        def has_permission(self, request, view):
            user = request.user
            if not user or not user.is_authenticated:
                return False
            if user.is_staff or user.is_superuser:
                return True
            return Permission.objects.filter(
                roles__users=user,
                code=self._code
            ).exists()

    _Perm.__name__ = f'RolePermission_{code.replace(":", "_")}'
    return _Perm
