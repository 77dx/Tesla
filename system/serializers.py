"""
@ Title:
@ Author: Cathy
@ Time: 2024/12/6 17:14
"""
from rest_framework import serializers
from .models import Department, Position, Role


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = "__all__"


class RoleSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer()
    # role = RoleSerializer()
    class Meta:
        model = Role
        fields = "__all__"





















