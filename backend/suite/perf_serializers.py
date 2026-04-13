"""
压测配置与结果序列化器
"""
from rest_framework import serializers
from .perf_models import PerformanceConfig, PerformanceResult


class PerformanceResultSerializer(serializers.ModelSerializer):
    duration       = serializers.FloatField(read_only=True)
    config_name    = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model  = PerformanceResult
        fields = [
            'id', 'config', 'config_name',
            'users', 'spawn_rate', 'run_time', 'host',
            'status', 'pid', 'error_msg',
            'summary', 'stats_data',
            'created_at', 'started_at', 'finished_at', 'duration',
            'created_by', 'created_by_name',
        ]
        read_only_fields = [
            'id', 'config', 'status', 'pid', 'error_msg',
            'summary', 'stats_data',
            'created_at', 'started_at', 'finished_at',
        ]

    def get_config_name(self, obj):
        return obj.config.display_name

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.username
        return None


class PerformanceResultBriefSerializer(serializers.ModelSerializer):
    """列表页嵌入用的简要序列化器"""
    duration = serializers.FloatField(read_only=True)

    class Meta:
        model  = PerformanceResult
        fields = [
            'id', 'status', 'users', 'spawn_rate', 'run_time', 'host',
            'summary', 'created_at', 'started_at', 'finished_at', 'duration',
        ]


class PerformanceConfigSerializer(serializers.ModelSerializer):
    suite_name    = serializers.CharField(source='suite.name', read_only=True)
    project_name  = serializers.CharField(source='project.name', read_only=True)
    display_name  = serializers.CharField(read_only=True)
    created_by_name = serializers.SerializerMethodField()
    latest_result = serializers.SerializerMethodField()
    result_count  = serializers.SerializerMethodField()

    class Meta:
        model  = PerformanceConfig
        fields = [
            'id', 'name', 'display_name',
            'suite', 'suite_name', 'project', 'project_name',
            'users', 'spawn_rate', 'run_time', 'host', 'case_ids',
            'created_at', 'updated_at',
            'created_by', 'created_by_name',
            'latest_result', 'result_count',
        ]
        read_only_fields = ['id', 'project', 'created_at', 'updated_at']

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.username
        return None

    def get_latest_result(self, obj):
        r = obj.results.order_by('-created_at').first()
        if r:
            return PerformanceResultBriefSerializer(r).data
        return None

    def get_result_count(self, obj):
        return obj.results.count()


class PerformanceConfigCreateSerializer(serializers.ModelSerializer):
    """创建/编辑配置"""
    class Meta:
        model  = PerformanceConfig
        fields = ['name', 'suite', 'users', 'spawn_rate', 'run_time', 'host', 'case_ids']
