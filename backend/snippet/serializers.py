"""
@ Title:
@ Author: Cathy
@ Time: 2024/12/16 11:20
"""
# from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework import serializers
from snippet.models import Snippet, LANGUAGE_CHOICES, STYLE_CHOICES

class SnippetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Snippet
        fields = '__all__'


# class SnippetSerializer(serializers.Serializer):
#     id = serializers.IntegerField(read_only=True)
#     title = serializers.CharField(required=False, allow_blank=True, max_length=100)
#     code = serializers.CharField(style={'base_template': 'textarea.html'})
#     linenos = serializers.BooleanField(required=False)
#     language = serializers.ChoiceField(choices=LANGUAGE_CHOICES, default='python')
#     style = serializers.ChoiceField(choices=STYLE_CHOICES, default='friendly')
#
#     def create(self, validated_data):
#         """
#         根据提供的验证过的数据创建并返回一个新的`Snippet`实例。
#         """
#         return Snippet.objects.create(**validated_data)
#
#     def update(self, instance, validated_data):
#         """
#         根据提供的验证过的数据更新和返回一个已经存在的`Snippet`实例。
#         """
#         instance.title = validated_data.get('title', instance.title)
#         instance.code = validated_data.get('code', instance.code)
#         instance.linenos = validated_data.get('linenos', instance.linenos)
#         instance.language = validated_data.get('language', instance.language)
#         instance.style = validated_data.get('style', instance.style)
#         instance.save()
#         return instance


















"""
注册和登录接口
注册
    1.校验两次密码一致
    2.注册接口无需校验登录
登录
    1.校验用户名和密码
    2.无需校验登录
    3.生成token
"""
# from rest_framework import serializers
# from django.contrib.auth.models import User
# from django.contrib.auth import authenticate
# from beifan.models import FeedBack
#
#
# class LoginSerializer(serializers.Serializer):
#     username = serializers.CharField(required=True)
#     password = serializers.CharField(required=True, write_only=True)  #设置 password 为 write_only=True，确保密码不会被序列化到响应中，增加安全性。
#
#     def validate(self, attrs):    # 功能： 用于验证整个数据字典。可以覆盖该方法以实现自定义验证逻辑。
#         username = attrs["username"]
#         password = attrs["password"]
#         print(attrs)
#
#         user = authenticate(username=username, password=password)
#
#         if not user:
#             raise serializers.ValidationError("用户名或密码错误！")
#         if not user.is_active:
#             raise serializers.ValidationError("用户状态已失效！")
#
#         attrs["user"] = user
#
#         return attrs
#
#     def to_representation(self, instance):    # 把token也封装进序列化中
#         # data = super().to_representation(instance)
#         data = {}
#         user = instance.get("user")
#         user_data = UserSerializer(user).data
#
#         # refresh = RefreshToken.for_user(user)
#         access = AccessToken.for_user(user)
#
#         data["token"] = access
#         data["userinfo"] = user_data
#         return data
#
#
# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         exclude = ["password"]
#
#     # def to_representation(self, instance):   # 添加额外的字段
#     #     data = super().to_representation(instance)   # instance是实例，也就是当前序列化的model的实例。
#     #     data['is_admin'] = instance.is_superuser  # 添加额外字段
#     #     data['auth'] = "cathy"
#     #     return data
#
# # serializers.ModelSerializer 会利用数据库的必填校验等规则
# class RegisterSerializer(serializers.ModelSerializer):
#     # feedback = FeedBackSerializer()    # 可以引用别的序列化实例
#
#     class Meta:
#         model = User
#         fields = '__all__'
#
#     password = serializers.CharField(required=True, max_length=128, write_only=True) # 该字段不会被序列化，不会返回
#     password_confirm = serializers.CharField(required=True, max_length=128, write_only=True)
#
#     def validate(self, attrs):    # attrs就是view中register接口的入参request.data
#         password = attrs["password"]
#         password_confirm = attrs.pop("password_confirm", None)    # 从 attrs 中移除, 否则在存储用户的时候会带着这个字段，而保存失败
#
#         if not attrs.get("email"):
#             raise serializers.ValidationError("邮箱不能为空！")
#         if password != password_confirm:
#             raise serializers.ValidationError("两次密码不一致！")
#
#         # try:
#         #     validate_password(password)
#         # except Exception as e:
#         #     raise serializers.ValidationError({"password": list(e.messages)})
#
#         return attrs
#
#     # 如果存在def validate_username：方法时，那么需要return username,否则username将无法正常序列化
#     def validate_username(self, username):   # def validate_<field_name>(attrs) 是个固定的用法，attrs的值去取决于field_name
#         if User.objects.filter(username=username):
#             raise serializers.ValidationError("用户名不能重复！")
#
#         return username
#
#     # def create(self, validated_data):
#     #     validated_data.pop("password_confirm", None)
#     #     user = User.objects.create_user(**validated_data)
#     #     return user
#
# class FeedBackAllSerializer(serializers.ModelSerializer):
#     # 获取feedback表中的所有数据
#     class Meta:
#         model = FeedBack
#         fields = '__all__'








