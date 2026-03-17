"""
@ Title:
@ Author: Cathy
@ Time: 2024/12/5 15:00
"""
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import Profile, Avatar
from system.models import Role, Department, Position
from rest_framework import serializers


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name"]

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
    avatar_url = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Avatar
        fields = ('user', 'avatar', 'avatar_url')
        extra_kwargs = {
            'avatar': {'write_only': True}  # avatar字段用于写入文件
        }

    def get_user(self, instance):
        return instance.id

    def get_avatar_url(self, instance):
        # 获取avatar字段的值（FileField的字符串表示）
        if not instance.avatar:
            return ''
        
        # 尝试构建完整URL
        request = self.context.get('request')
        if request:
            # 使用request.build_absolute_uri构建完整URL
            return request.build_absolute_uri(instance.avatar.url)
        else:
            # 没有request上下文，返回相对路径
            return instance.avatar.name
    
    def create(self, validated_data):
        # 从上下文中获取当前用户
        request = self.context.get('request')
        if request and request.user:
            validated_data['user'] = request.user
        return super().create(validated_data)

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


class UserProfileAdminSerializer(serializers.ModelSerializer):
    """管理员视角的用户信息序列化器（含部门、职位、角色）"""
    username = serializers.CharField(source='user.username', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    is_staff = serializers.BooleanField(source='user.is_staff', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True, default=None)
    position_name = serializers.CharField(source='position.name', read_only=True, default=None)
    role_list = serializers.SerializerMethodField(read_only=True)

    # 写入字段
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), required=False, allow_null=True
    )
    position = serializers.PrimaryKeyRelatedField(
        queryset=Position.objects.all(), required=False, allow_null=True
    )
    role_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, write_only=True,
        help_text='角色 id 列表，传入后全量替换用户角色'
    )

    class Meta:
        model = Profile
        fields = [
            'user_id', 'username', 'is_staff',
            'nickname', 'avatar_url',
            'department', 'department_name',
            'position', 'position_name',
            'role_list', 'role_ids',
        ]

    def get_role_list(self, instance):
        roles = Role.objects.filter(users=instance.user)
        return [{'id': r.id, 'name': r.name} for r in roles]

    def update(self, instance, validated_data):
        role_ids = validated_data.pop('role_ids', None)
        # 更新部门/职位（department 变化会触发 Profile.save() 自动同步 default_role）
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        # 全量替换角色（在 default_role 同步后叠加手动角色）
        if role_ids is not None:
            from system.models import User_Role
            # 保留 default_role 关联，只替换手动分配的角色
            dept = instance.department
            default_role = dept.default_role if dept else None
            # 清除所有角色后重设
            instance.user.roles.clear()
            if default_role:
                instance.user.roles.add(default_role)
            valid_roles = Role.objects.filter(id__in=role_ids)
            instance.user.roles.add(*valid_roles)
        return instance






















