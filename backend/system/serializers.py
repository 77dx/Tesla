"""
@ Title:
@ Author: Cathy
@ Time: 2024/12/6 17:14
"""
from django.core.exceptions import ObjectDoesNotExist
from Tesla import settings
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Department, Position, Role, Permission


class DepartmentSerializer(serializers.ModelSerializer):
    """部门信息"""
    class Meta:
        model = Department
        fields = '__all__'

class DepartmentListSerializer(serializers.ModelSerializer):
    # 部门管理的列表字段有：部门名称name, 部门简介intro, 主管头像avatar, 部门主管leader_name
    class Meta:
        model = Department
        fields = ['id', 'name', 'intro', 'avatar', 'leader', 'leader_name', 'default_role', 'default_role_name']  # 列表字段
        extra_kwargs = {
            'leader': {'queryset': User.objects.select_related('profile')} # 关联字段
        }
    # 定义主管头像字段
    avatar = serializers.SerializerMethodField(read_only=True)
    # 定义主管名字字段
    leader_name = serializers.SerializerMethodField(read_only=True)
    # 默认角色名称
    default_role_name = serializers.CharField(source='default_role.name', read_only=True, default=None)

    # avatar字段的对应方法
    def get_avatar(self, instance):
        # 反射，找到leader的用户对象
        leader = getattr(instance, 'leader', None)
        if leader is None:
            return settings.DEFAULT_AVATAR_URL
        # 处理空的头像地址
        try:
            return leader.profile.avatar_url
        except (ObjectDoesNotExist, AttributeError):
            return settings.DEFAULT_AVATAR_URL

    # leader_name字段对应的获取方法
    def get_leader_name(self, instance):
        leader = getattr(instance, 'leader', None)
        return getattr(leader, 'username', None) if leader else None

class DepartmentDeleteSerializer(serializers.Serializer):
    """删除部门"""
    id = serializers.IntegerField(
        min_value=1,
        max_value=999,
        error_messages={
            'invalid': '部门ID必须为数字',
            'required': '部门id不能为空',
            'min_value': '部门id必须大于0',
            'max_value': '部门id必须小于999'
        }
    )

    def validate_id(self, value):
        if not Department.objects.filter(id=value).exists():
            raise serializers.ValidationError("部门不存在")
        return value


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = "__all__"


class RoleSerializer(serializers.ModelSerializer):
    user_count = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = "__all__"

    def get_user_count(self, obj):
        return obj.users.count()

class AssignRoleSerializer(serializers.Serializer):
    role_id = serializers.IntegerField(
        error_messages={
            'invalid': '角色ID必须为数字',
            'required': '角色id不能为空'
        }
    )
    user_ids = serializers.ListField(
        error_messages={
            'required': '用户id不能为空'
        }
    )

    def validate_role_id(self, value):
        if not Role.objects.filter(id=value).exists():
            raise serializers.ValidationError("角色不存在")
        return value

    def validate_user_ids(self, value):
        existing_user_ids = set(User.objects.filter(id__in=value).values_list('id', flat=True))
        non_existing_user_ids = set(value) - existing_user_ids

        if non_existing_user_ids:
            raise serializers.ValidationError(f"用户ID不存在：{non_existing_user_ids}")

        return list(User.objects.filter(id__in=existing_user_ids))



class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username']


class PermissionSerializer(serializers.ModelSerializer):
    """权限码序列化器"""
    class Meta:
        model = Permission
        fields = ['id', 'code', 'name', 'module']


class PermissionGroupSerializer(serializers.Serializer):
    """按模块分组的权限列表（供前端权限配置弹窗使用）"""
    module = serializers.CharField()
    permissions = PermissionSerializer(many=True)


class RoleDetailSerializer(serializers.ModelSerializer):
    """角色详情：含权限列表和用户列表"""
    permissions = PermissionSerializer(many=True, read_only=True)
    user_count = serializers.SerializerMethodField()
    permission_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text='权限 id 列表，传入后全量替换角色权限'
    )

    class Meta:
        model = Role
        fields = ['id', 'name', 'created_at', 'user_count', 'permissions', 'permission_ids']

    def get_user_count(self, obj):
        return obj.users.count()

    def update(self, instance, validated_data):
        permission_ids = validated_data.pop('permission_ids', None)
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        if permission_ids is not None:
            perms = Permission.objects.filter(id__in=permission_ids)
            instance.permissions.set(perms)
        return instance


class SetPermissionsSerializer(serializers.Serializer):
    """给角色批量设置权限"""
    permission_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text='权限 id 列表（全量替换）'
    )

    def validate_permission_ids(self, value):
        existing = set(Permission.objects.filter(id__in=value).values_list('id', flat=True))
        missing = set(value) - existing
        if missing:
            raise serializers.ValidationError(f'权限 ID 不存在：{missing}')
        return value


class DepartmentDetailSerializer(serializers.ModelSerializer):
    """部门详情：含 default_role 字段"""
    default_role_name = serializers.CharField(source='default_role.name', read_only=True, default=None)
    default_role = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Department
        fields = ['id', 'name', 'intro', 'leader', 'default_role', 'default_role_name', 'created_at']











