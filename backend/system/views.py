import logging
from collections import defaultdict

from django.contrib.auth.models import User
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.response import Response
from Tesla.customPagination import CustomPageNumberPagination
from snippet.base_viewset import BaseViewSet
from .models import Department, Position, Role, Permission
from .serializers import (
    DepartmentDeleteSerializer, DepartmentSerializer, DepartmentListSerializer,
    DepartmentDetailSerializer, PositionSerializer, RoleSerializer, RoleDetailSerializer,
    AssignRoleSerializer, UserSerializer, PermissionSerializer, SetPermissionsSerializer,
)


@extend_schema(tags=["System"])
class DepartmentViewSet(BaseViewSet):
    serializer_class = DepartmentDetailSerializer
    pagination_class = CustomPageNumberPagination
    search_fields = ['name']
    product_line_field = None

    def get_queryset(self):
        return Department.objects.all().order_by('-id')

    def get_serializer_class(self):
        if self.action == "list":
            return DepartmentListSerializer
        return DepartmentDetailSerializer

    @action(methods=['POST'], detail=False, url_path="delete")
    def department_delete(self, request):
        serializer = DepartmentDeleteSerializer(data=request.data)
        if not serializer.is_valid():
            errors = serializer.errors.get('id', [])
            error_message = errors[0] if errors else '删除失败'
            return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)
        department_id = serializer.validated_data.get('id')
        department = Department.objects.get(id=department_id)
        department_name = department.name
        department.delete()
        return Response({f"detail": f"{department_name}, 删除成功", "id": department_id}, status=status.HTTP_200_OK)


@extend_schema(tags=["System"])
class PositionViewSet(BaseViewSet):
    serializer_class = PositionSerializer
    pagination_class = CustomPageNumberPagination
    search_fields = ['name']
    product_line_field = None

    def get_queryset(self):
        qs = Position.objects.all().order_by('-id')
        is_leader = self.request.query_params.get('is_leader', '')
        if is_leader == 'true':
            qs = qs.filter(is_leader=True)
        elif is_leader == 'false':
            qs = qs.filter(is_leader=False)
        return qs


@extend_schema(tags=["System"])
class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """权限码管理（只读，数据由 init_permissions 命令初始化）"""
    queryset = Permission.objects.all().order_by('module', 'code')
    serializer_class = PermissionSerializer
    pagination_class = None  # 权限码数量有限，不分页

    @action(methods=['GET'], detail=False, url_path='grouped')
    def grouped(self, request):
        """按模块分组返回所有权限码（供前端配置弹窗使用）"""
        groups = defaultdict(list)
        for perm in Permission.objects.all().order_by('module', 'code'):
            groups[perm.module].append(PermissionSerializer(perm).data)
        result = [
            {'module': module, 'permissions': perms}
            for module, perms in groups.items()
        ]
        return Response(result)


@extend_schema(tags=["System"])
class RoleViewSet(BaseViewSet):
    serializer_class = RoleSerializer
    pagination_class = CustomPageNumberPagination
    search_fields = ['name']
    product_line_field = None
    queryset = Role.objects.all().order_by('-id')
    queryset = Role.objects.all().order_by('-id')

    def get_serializer_class(self):
        if self.action in ('retrieve', 'set_permissions', 'partial_update', 'update'):
            return RoleDetailSerializer
        return RoleSerializer

    # ── 给角色添加用户 ──
    @action(methods=['POST'], detail=False, url_path="assign_role")
    def assign_role(self, request):
        serializer = AssignRoleSerializer(data=request.data)
        if serializer.is_valid():
            users = serializer.validated_data['user_ids']
            role_id = serializer.validated_data['role_id']
            role = Role.objects.get(id=role_id)
            role.users.add(*users)
            return Response({"detail": "角色分配成功", "role": RoleSerializer(role).data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ── 查询用户角色 ──
    @action(methods=['POST'], detail=False, url_path="get_user_roles")
    def get_user_roles(self, request):
        user_id = request.data.get('user_id')
        return Response({"roles": RoleSerializer(Role.objects.filter(users=user_id), many=True).data})

    # ── 查询角色的用户列表 ──
    @action(methods=['POST'], detail=False, url_path="get_role_users")
    def get_role_users(self, request):
        role_id = request.data.get('role_id')
        return Response({"users": UserSerializer(User.objects.filter(roles=role_id), many=True).data})

    # ── 给角色全量设置权限 ──
    @action(methods=['POST'], detail=True, url_path='set_permissions')
    def set_permissions(self, request, pk=None):
        """全量替换角色的权限列表"""
        role = self.get_object()
        serializer = SetPermissionsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        perms = Permission.objects.filter(id__in=serializer.validated_data['permission_ids'])
        role.permissions.set(perms)
        return Response(RoleDetailSerializer(role).data)

    # ── 获取角色当前权限列表 ──
    @action(methods=['GET'], detail=True, url_path='permissions')
    def get_permissions_list(self, request, pk=None):
        """返回角色已配置的权限列表"""
        role = self.get_object()
        return Response(PermissionSerializer(role.permissions.all(), many=True).data)

    # ── 给角色全量设置用户 ──
    @action(methods=['POST'], detail=True, url_path='set_users')
    def set_users(self, request, pk=None):
        """全量替换角色的用户列表"""
        role = self.get_object()
        user_ids = request.data.get('user_ids', [])
        existing_users = User.objects.filter(id__in=user_ids)
        missing = set(user_ids) - set(existing_users.values_list('id', flat=True))
        if missing:
            return Response({'error': f'用户 ID 不存在：{missing}'}, status=status.HTTP_400_BAD_REQUEST)
        role.users.set(existing_users)
        return Response({"detail": "用户设置成功", "user_count": role.users.count()})
