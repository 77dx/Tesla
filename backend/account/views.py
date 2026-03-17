from django.core.serializers import serialize
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.authtoken.admin import User
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import LoginSerializer, ProfileSerializer, ResetPasswordSerializer, ModifySerializer, \
    AvatarSerializer, UserNameSerializer, UserProfileAdminSerializer
from .models import Profile, Avatar
from drf_spectacular.utils import extend_schema
from system.models import Permission

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
        profile, _ = Profile.objects.get_or_create(user=serializer.validated_data['user'])
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
            # 验证旧密码
            old_password = serializer.validated_data['old_password']
            if not user.check_password(old_password):
                return Response({"status": "旧密码错误"}, status=status.HTTP_400_BAD_REQUEST)
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
        serializer = AvatarSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        avatar_instance = serializer.save()
        
        # 返回完整的响应，包括avatar_url
        return Response(serializer.data)

    @action(methods=['GET'], detail=False)
    def get_all_users(self, request):
        users = User.objects.all()
        serializer = UserNameSerializer(users, many=True)
        usernames = [{"id": item['id'],"username": item['username']} for item in serializer.data]
        return Response(usernames)

    @extend_schema(summary="获取当前用户权限码列表")
    @action(methods=['GET'], detail=False, url_path='my_permissions')
    def my_permissions(self, request):
        """返回当前用户拥有的所有权限码。管理员返回 ["*"] 表示拥有所有权限。"""
        user = request.user
        if user.is_staff or user.is_superuser:
            return Response(["*"])
        # 聚合用户所有角色的权限码
        codes = list(
            Permission.objects.filter(roles__users=user)
            .values_list('code', flat=True)
            .distinct()
        )
        return Response(codes)


@extend_schema(tags=['Account'])
class UserProfileAdminViewSet(viewsets.GenericViewSet):
    """管理员用户管理：查看所有用户信息、修改部门/职位/角色"""
    parser_classes = [JSONParser]

    @action(methods=['GET'], detail=False, url_path='list')
    def user_list(self, request):
        """获取所有用户的详细信息（含部门、职位、角色）"""
        profiles = Profile.objects.select_related(
            'user', 'department', 'position'
        ).prefetch_related('user__roles').all().order_by('id')
        serializer = UserProfileAdminSerializer(profiles, many=True)
        return Response(serializer.data)

    @action(methods=['POST'], detail=False, url_path='update')
    def update_user(self, request):
        """修改用户的部门、职位、角色（管理员专用）"""
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'user_id 不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            profile = Profile.objects.select_related('department').get(user_id=user_id)
        except Profile.DoesNotExist:
            return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserProfileAdminSerializer(
            instance=profile, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)




















