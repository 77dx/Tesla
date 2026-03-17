"""
@ Title:
@ Author: Cathy
@ Time: 2024/12/9 14:13
"""
from rest_framework import serializers
from .models import Project, Config


class ProjectSerializer(serializers.ModelSerializer):
    intro = serializers.CharField(required=False, default='', allow_blank=True)
    url = serializers.CharField(required=False, default='', allow_blank=True)
    pm_name = serializers.SerializerMethodField(read_only=True)
    product_line_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Project
        fields = "__all__"

    def get_pm_name(self, obj):
        if obj.pm:
            try:
                return obj.pm.profile.nickname or obj.pm.username
            except Exception:
                return obj.pm.username
        return None

    def get_product_line_name(self, obj):
        return obj.product_line.name if obj.product_line else None


class ConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = Config
        fields = "__all__"