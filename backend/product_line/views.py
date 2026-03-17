from django.contrib.auth.models import User
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import ProductLine, ProductLineMember
from .serializers import ProductLineSerializer, ProductLineMemberSerializer


@extend_schema(tags=['ProductLine'])
class ProductLineViewSet(viewsets.ModelViewSet):
    serializer_class = ProductLineSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # 超管看全部，普通用户只看自己所属产品线
        if user.roles.filter(permissions__code='*').exists() or \
                user.roles.filter(name__in=['超级管理员', 'admin']).exists():
            return ProductLine.objects.all().order_by('id')
        return ProductLine.objects.filter(members__user=user).order_by('id')

    def perform_create(self, serializer):
        pl = serializer.save(created_by=self.request.user)
        # 创建者自动成为成员（无角色，可后续设置）
        ProductLineMember.objects.get_or_create(product_line=pl, user=self.request.user)

    @action(methods=['GET'], detail=False, url_path='mine')
    def mine(self, request):
        """我所属的产品线列表"""
        qs = ProductLine.objects.filter(members__user=request.user).order_by('id')
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(methods=['GET'], detail=True, url_path='permissions')
    def my_permissions(self, request, pk=None):
        """我在该产品线的权限码列表"""
        pl = self.get_object()
        # 超管直接返回 '*'
        if request.user.roles.filter(permissions__code='*').exists():
            return Response(['*'])
        try:
            membership = pl.members.get(user=request.user)
            codes = membership.get_permissions()
        except ProductLineMember.DoesNotExist:
            codes = []
        return Response(codes)

    @action(methods=['GET', 'POST'], detail=True, url_path='members')
    def members(self, request, pk=None):
        """获取或添加产品线成员"""
        pl = self.get_object()
        if request.method == 'GET':
            qs = pl.members.select_related('user', 'role').all()
            serializer = ProductLineMemberSerializer(qs, many=True)
            return Response(serializer.data)
        # POST: 添加成员
        user_id = request.data.get('user')
        role_id = request.data.get('role')
        if not user_id:
            return Response({'msg': 'user 字段必填'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'msg': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
        member, created = ProductLineMember.objects.get_or_create(
            product_line=pl, user=user
        )
        if role_id:
            from system.models import Role
            try:
                member.role = Role.objects.get(id=role_id)
                member.save(update_fields=['role'])
            except Role.DoesNotExist:
                pass
        serializer = ProductLineMemberSerializer(member)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(methods=['DELETE'], detail=True, url_path='members/(?P<member_id>[0-9]+)')
    def remove_member(self, request, pk=None, member_id=None):
        """移除产品线成员"""
        pl = self.get_object()
        try:
            member = pl.members.get(id=member_id)
            member.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ProductLineMember.DoesNotExist:
            return Response({'msg': '成员不存在'}, status=status.HTTP_404_NOT_FOUND)

    @action(methods=['PATCH'], detail=True, url_path='members/(?P<member_id>[0-9]+)/role')
    def update_member_role(self, request, pk=None, member_id=None):
        """更新成员角色"""
        pl = self.get_object()
        try:
            member = pl.members.get(id=member_id)
        except ProductLineMember.DoesNotExist:
            return Response({'msg': '成员不存在'}, status=status.HTTP_404_NOT_FOUND)
        role_id = request.data.get('role')
        if role_id:
            from system.models import Role
            try:
                member.role = Role.objects.get(id=role_id)
            except Role.DoesNotExist:
                return Response({'msg': '角色不存在'}, status=status.HTTP_404_NOT_FOUND)
        else:
            member.role = None
        member.save(update_fields=['role'])
        return Response(ProductLineMemberSerializer(member).data)
