from django.contrib.auth.models import User
from rest_framework import serializers
from .models import ProductLine, ProductLineMember
from system.models import Role


class ProductLineMemberSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    nickname = serializers.SerializerMethodField(read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)

    class Meta:
        model = ProductLineMember
        fields = ['id', 'product_line', 'user', 'username', 'nickname', 'role', 'role_name', 'joined_at']
        extra_kwargs = {
            'product_line': {'required': True},
            'user': {'required': True},
        }

    def get_nickname(self, obj):
        try:
            return obj.user.profile.nickname
        except Exception:
            return obj.user.username


class ProductLineSerializer(serializers.ModelSerializer):
    members_count = serializers.SerializerMethodField(read_only=True)
    created_by_name = serializers.SerializerMethodField(read_only=True)
    my_role = serializers.SerializerMethodField(read_only=True)
    my_role_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ProductLine
        fields = ['id', 'name', 'description', 'created_by', 'created_by_name',
                  'created_at', 'members_count', 'my_role', 'my_role_name']
        extra_kwargs = {'created_by': {'read_only': True}}

    def get_members_count(self, obj):
        return obj.members.count()

    def get_created_by_name(self, obj):
        return obj.created_by.username if obj.created_by else None

    def _get_membership(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        return obj.members.filter(user=request.user).first()

    def get_my_role(self, obj):
        m = self._get_membership(obj)
        return m.role_id if m else None

    def get_my_role_name(self, obj):
        m = self._get_membership(obj)
        return m.role.name if m and m.role else None
