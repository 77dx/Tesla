"""
性能测试序列化器
"""
from rest_framework import serializers
from .performance_models import PerformanceTest


class PerformanceTestSerializer(serializers.ModelSerializer):
    suite_name   = serializers.CharField(source='suite.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    created_by_name = serializers.SerializerMethodField()
    duration     = serializers.FloatField(read_only=True)

    class Meta:
        model  = PerformanceTest
        fields = [
            'id', 'name', 'suite', 'suite_name', 'project', 'project_name',
            'users', 'spawn_rate', 'run_time', 'host', 'case_ids',
            'status', 'pid', 'error_msg',
            'summary', 'stats_data',
            'created_at', 'started_at', 'finished_at', 'duration',
            'created_by', 'created_by_name',
        ]
        read_only_fields = [
            'id', 'status', 'pid', 'error_msg', 'summary', 'stats_data',
            'created_at', 'started_at', 'finished_at',
        ]

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.username
        return None


class PerformanceTestCreateSerializer(serializers.ModelSerializer):
    """创建性能测试时使用的序列化器（只需传入配置参数）"""
    class Meta:
        model  = PerformanceTest
        fields = ['name', 'suite', 'users', 'spawn_rate', 'run_time', 'host', 'case_ids']
