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

    class Meta:
        model = Project
        fields = "__all__"


class ConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = Config
        fields = "__all__"