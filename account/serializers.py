"""
@ Title:
@ Author: Cathy
@ Time: 2024/12/5 15:00
"""
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import Profile, Avatar
from system.models import Role
from rest_framework import serializers


class RoleSerializer(serializers.ModelSerializer):
    # name = serializers.CharField(source='role.name')
    # members = serializers.SerializerMethodField(source='User')
    department = serializers.CharField(source='department.name')
    position = serializers.CharField(source='position.name')
    is_leader = serializers.BooleanField(source='position.is_leader')

    class Meta:
        model = Role
        fields = ["department", "position", "is_leader"]

class UserSerializer(serializers.ModelSerializer):
    """Django自带的user"""
    class Meta:
        model = User
        fields = ('username', 'email', 'is_active')

class ProfileSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()
    role_list = RoleSerializer(read_only=True, many=True, source='get_role_list')
    userInfo = serializers.SerializerMethodField(read_only=True)  # SerializerMethodField,DRF会自动调用get_user方法。

    class Meta:
        model = Profile
        fields = '__all__'

    # get_字段名，DRF会自动调用(使用SerializerMethodField的话)
    def get_token(self, instance):
        user = instance.user
        token, _ = Token.objects.get_or_create(user=user)
        return token.key

    def get_userInfo(self, instance):
        return UserSerializer(instance.user).data

    def get_role_list(self, instance):
        return instance

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    # 校验登录数据
    def validate(self, attrs):
        username = attrs['username']
        password = attrs['password']
        user = authenticate(username=username, password=password)
        if not user:
            from rest_framework.exceptions import AuthenticationFailed
            raise AuthenticationFailed("用户名或密码错误")
        attrs["user"] = user
        return attrs

class ResetPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, min_length=6)
    new_password = serializers.CharField(required=True, min_length=6)

    def validate(self, attrs):
        old_password = attrs["old_password"]
        new_password = attrs["new_password"]
        if old_password == new_password:
            raise serializers.ValidationError("新旧密码一致，请重新输入")
        return attrs

class AvatarSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    class Meta:
        model = Avatar
        fields = ('user', 'avatar')

    def get_user(self, instance):
        return instance.id

class ModifySerializer(serializers.ModelSerializer):
    # 表单数据 write_only=True
    nickname = serializers.CharField(required=True, write_only=True)
    avatar_url = serializers.CharField(required=True, write_only=True)
    # 响应数据 read_only=True
    profile = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Profile
        fields = ['nickname', 'avatar_url', 'profile']

    def get_profile(self, instance):
        return ProfileSerializer(instance, context=self.context).data

class UserNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username']






















