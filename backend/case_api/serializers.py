"""
@ Title:
@ Author: Cathy
@ Time: 2024/12/9 15:20
"""
from rest_framework import serializers
from .models import Endpoint, Case, CaseNode
from project.models import Project
from product_line.models import ProductLine

class EndpointSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    product_line_name = serializers.CharField(source='product_line.name', read_only=True)
    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(),
        required=False, allow_null=True, default=None
    )
    product_line = serializers.PrimaryKeyRelatedField(
        queryset=ProductLine.objects.all(),
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
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all(), required=False, allow_null=True)
    product_line = serializers.PrimaryKeyRelatedField(queryset=ProductLine.objects.all(), required=False, allow_null=True)
    # 添加项目名称字段
    project_name = serializers.CharField(source='project.name', read_only=True)
    product_line_name = serializers.CharField(source='product_line.name', read_only=True)
    created_by_name = serializers.SerializerMethodField(read_only=True)
    sprint_name = serializers.SerializerMethodField(read_only=True)
    requirement_title = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Case
        fields = "__all__"

    def get_created_by_name(self, obj):
        return obj.updated_by.username if obj.updated_by else (obj.created_by.username if obj.created_by else None)

    def get_sprint_name(self, obj):
        return obj.sprint.name if obj.sprint else None

    def get_requirement_title(self, obj):
        return obj.requirement.title if obj.requirement else None

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
        data['product_line_name'] = instance.product_line.name if instance.product_line else None
        return data

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        instance.version = (instance.version or 1) + 1
        obj = super().update(instance, validated_data)
        obj.save(update_fields=['version'])
        return obj


class CaseNodeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    item = serializers.SerializerMethodField()

    class Meta:
        model = CaseNode
        fields = ['id', 'name', 'parent', 'path', 'node_type', 'case', 'order_no', 'children', 'item']

    def get_children(self, obj):
        children = obj.children.all().order_by('order_no', 'id')
        return CaseNodeSerializer(children, many=True).data

    def get_item(self, obj):
        if obj.node_type == CaseNode.NodeType.CASE and obj.case:
            return {'id': obj.case.id, 'name': obj.case.name}
        return None
