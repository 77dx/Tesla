"""
@ Title:
@ Author: Cathy
@ Time: 2024/12/9 15:20
"""
from rest_framework import serializers
from .models import Endpoint, Case


class EndpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Endpoint
        fields = "__all__"

class EndpointNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Endpoint
        fields = ['id', 'name']


class CaseSerializer(serializers.ModelSerializer):
    # 通过自定义逻辑实现：输入时接收 endpoint ID，输出时展示嵌套数据
    endpoint = serializers.PrimaryKeyRelatedField(
        queryset=Endpoint.objects.all(),
        write_only=True)  # 仅在写入时使用，输入格式为 ID

    class Meta:
        model = Case
        fields = "__all__"

    def to_representation(self, instance):
        # 获取默认序列化结果
        data = super().to_representation(instance)
        # 将 endpoint ID 替换为完整的 Endpoint 序列化数据
        data['endpoint'] = EndpointNameSerializer(instance.endpoint).data
        return data
