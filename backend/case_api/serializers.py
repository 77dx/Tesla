"""
@ Title:
@ Author: Cathy
@ Time: 2024/12/9 15:20
"""
from rest_framework import serializers
from .models import Endpoint, Case
from project.models import Project

class EndpointSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(),
        required=False, allow_null=True, default=None
    )
    created_by_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Endpoint
        fields = "__all__"

    def get_created_by_name(self, obj):
        return obj.updated_by.username if obj.updated_by else (obj.created_by.username if obj.created_by else None)

class EndpointNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Endpoint
        fields = ['id', 'name']

class EndpointDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Endpoint
        fields = ['id', 'name', 'method', 'url', 'service_key', 'headers', 'params', 'data', 'json', 'cookies']

class CaseSerializer(serializers.ModelSerializer):
    # 通过自定义逻辑实现：输入时接收 endpoint ID，输出时展示嵌套数据
    endpoint = serializers.PrimaryKeyRelatedField(
        queryset=Endpoint.objects.all(),
        write_only=True)  # 仅在写入时使用，输入格式为 ID
    # 添加项目名称字段
    project_name = serializers.CharField(source='project.name', read_only=True)
    created_by_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Case
        fields = "__all__"

    def get_created_by_name(self, obj):
        return obj.updated_by.username if obj.updated_by else (obj.created_by.username if obj.created_by else None)

    def to_representation(self, instance):
        # 获取默认序列化结果
        data = super().to_representation(instance)
        # 将 endpoint ID 替换为完整的 Endpoint 序列化数据
        data['endpoint'] = EndpointDetailSerializer(instance.endpoint).data
        # 确保 project_name 字段存在
        if instance.project:
            data['project_name'] = instance.project.name
            data['project_product_line'] = instance.project.product_line_id
        else:
            data['project_name'] = ''
            data['project_product_line'] = None
        return data
