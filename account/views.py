from django.core.serializers import serialize
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.authtoken.admin import User
from rest_framework.decorators import action, permission_classes
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import LoginSerializer, ProfileSerializer, ResetPasswordSerializer, ModifySerializer, \
    AvatarSerializer, UserNameSerializer
from .models import Profile, Avatar
from drf_spectacular.utils import extend_schema

@extend_schema(
    tags=['Account']
)
class ProfileViewSet(viewsets.GenericViewSet):
    # ----- 全局默认只支持 application/json -----
    parser_classes = [JSONParser]

    @extend_schema(
        request=LoginSerializer,
        responses=ProfileSerializer,
    )
    @action(methods=['POST'], detail=False, permission_classes=[AllowAny])
    def login(self, request):
        """用户登录"""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = Profile.objects.get(user=serializer.validated_data['user'])
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=ResetPasswordSerializer,
        responses=ResetPasswordSerializer
    )
    @action(methods=['POST'], detail=False)
    def reset_password(self, request):
        """重置密码"""
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if user := request.user:
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            # serializer = ProfileSerializer(user)
            return Response({"status": "修改成功", "data": None})
        return Response({"status": "fail"})

    @extend_schema(
        request=ProfileSerializer,
        responses=ProfileSerializer
    )
    @action(methods=['GET'], detail=False)
    def profile(self, request):
        """用户信息"""
        profile, _ = Profile.objects.get_or_create(user=request.user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    @extend_schema(
        request=ModifySerializer,
        responses=ModifySerializer,
    )
    @action(methods=['POST'], detail=False) # ← 仅 modify 使用 form-data)
    def modify(self, request):
        """修改用户信息"""
        profile = Profile.objects.get(user=request.user)
        serializer = ModifySerializer(instance=profile, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(
        request=AvatarSerializer,
        responses=AvatarSerializer,
    )
    @action(methods=['POST'], detail=False, parser_classes=[MultiPartParser, FormParser])
    def img_upload(self, request):
        obj = Avatar.objects.create(user=request.user)
        serializer = AvatarSerializer(obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    @action(methods=['GET'], detail=False)
    def get_all_users(self, request):
        users = User.objects.all()
        serializer = UserNameSerializer(users, many=True)
        usernames = [{"id": item['id'],"username": item['username']} for item in serializer.data]
        return Response(usernames)




















