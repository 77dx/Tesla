"""
@ Title:
@ Author: Cathy
@ Time: 2024/12/5 15:00
"""
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import Profile
from system.models import Role
from rest_framework import serializers


class RoleSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='role.name')
    members = serializers.SerializerMethodField(source='User')
    # department_id = serializers.CharField(source='department.name')
    # position_id = serializers.CharField(source='position.name')

    class Meta:
        model = Role
        fields = ["name", "members"]


class ProfileSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    role_list = RoleSerializer(read_only=True, many=True, source="get_role_list")

    class Meta:
        model = Profile
        fields = '__all__'

    def get_token(self, obj):
        user = obj.user
        token, create = Token.objects.get_or_create(user=user)

        return token.key

    def get_user(self, obj):
        return obj.user_id

    def get_role_list(self, obj):
        return obj


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate_username(self, username):
        return username

    def validate(self, attrs):
        username = attrs['username']
        password = attrs['password']

        user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError("用户名密码错误")
        else:
            Profile.objects.get_or_create(user=user)
            token, create = Token.objects.get_or_create(user=user)

            attrs["user"] = user

            return attrs

class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True, min_length=6)
    confirm_password = serializers.CharField(required=True, min_length=6)

    def validate(self, attrs):
        new_password = attrs["new_password"]
        confirm_password = attrs["confirm_password"]

        if new_password != confirm_password:
            raise serializers.ValidationError("两次密码不一致")

        return attrs




















