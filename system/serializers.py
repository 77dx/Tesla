"""
@ Title:
@ Author: Cathy
@ Time: 2024/12/6 17:14
"""
from django.core.exceptions import ObjectDoesNotExist

from Tesla import settings
from account.models import Profile
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Department, Position, Role


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class DepartmentListSerializer(serializers.ModelSerializer):
    '''
        部门管理的列表字段有：部门名称name, 部门简介intro, 主管头像avatar, 部门主管leader_name
    '''
    # 设置字段
    class Meta:
        model = Department
        fields = ['id', 'name', 'intro', 'avatar', 'leader', 'leader_name']  # 列表字段
        extra_kwargs = {
            'leader': {'queryset': User.objects.select_related('profile')} # 关联字段
        }
    # 定义主管头像字段
    avatar = serializers.SerializerMethodField(read_only=True)
    # 定义主管名字字段
    leader_name = serializers.SerializerMethodField(read_only=True)

    # avatar字段的对应方法
    def get_avatar(self, instance):
        # 反射，找到leader的用户对象
        leader = getattr(instance, 'leader', None)
        # 处理空的头像地址
        try:
            return leader.profile.avatar_url
        except ObjectDoesNotExist:
            return settings.DEFAULT_AVATAR_URL

    # leader_name字段对应的获取方法
    def get_leader_name(self, instance):
        leader = getattr(instance, 'leader', None)
        return getattr(leader, 'username', None) if leader else None

class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = "__all__"


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"





















