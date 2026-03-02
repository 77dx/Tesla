import logging

from django.contrib.auth.models import User
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.response import Response
from Tesla.customPagination import CustomPageNumberPagination
from .models import Department, Position, Role
from .serializers import DepartmentDeleteSerializer, DepartmentSerializer, DepartmentListSerializer, PositionSerializer, \
    RoleSerializer, AssignRoleSerializer, UserSerializer


@extend_schema(tags=["System"])
class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all().order_by('-id')
    serializer_class = DepartmentSerializer
    pagination_class = CustomPageNumberPagination

    def get_serializer_class(self):
        if self.action == "list":
            return DepartmentListSerializer
        return super().get_serializer_class()
    
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
        # 删除成功，返回成功消息，也可以返回被删除的id
        return Response({f"detail": f"{department_name}, 删除成功", "id": department_id}, status=status.HTTP_200_OK)

@extend_schema(tags=["System"])
class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer

@extend_schema(tags=["System"])
class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

    # 给角色添加用户
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

    # 查询用户角色
    @action(methods=['POST'], detail=False, url_path="get_user_roles")
    def get_user_roles(self, request):
        user_id = request.data.get('user_id')
        return Response({"roles": RoleSerializer(Role.objects.filter(users=user_id), many=True).data})

    # 查询角色的用户列表
    @action(methods=['POST'], detail=False, url_path="get_role_users")
    def get_role_users(self, request):
        role_id = request.data.get('role_id')
        return Response({"users": UserSerializer(User.objects.filter(roles=role_id), many=True).data})




