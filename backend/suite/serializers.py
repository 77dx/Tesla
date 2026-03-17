"""
套件序列化器
"""
from pathlib import Path
from rest_framework import serializers
from case_api.models import Case as CaseAPI
from case_ui.models import Case as CaseUI
from .models import Suite, SuiteCaseItem, RunResult, Environment, GlobalVariable, Service


class ServiceSerializer(serializers.ModelSerializer):
    project_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Service
        fields = ['id', 'key', 'name', 'description', 'project', 'project_name', 'created_at']

    def get_project_name(self, obj):
        return obj.project.name if obj.project else None


class EnvironmentSerializer(serializers.ModelSerializer):
    project_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Environment
        fields = ['id', 'name', 'project', 'project_name', 'base_url', 'urls',
                  'headers', 'variables', 'description', 'created_at']

    def get_project_name(self, obj):
        return obj.project.name if obj.project else None


class GlobalVariableSerializer(serializers.ModelSerializer):
    environment_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = GlobalVariable
        fields = ['id', 'environment', 'environment_name', 'key', 'value', 'description', 'created_at']

    def get_environment_name(self, obj):
        return obj.environment.name if obj.environment else None


class SuiteCaseItemSerializer(serializers.ModelSerializer):
    """套件用例项序列化器"""
    # 只读展示字段
    case_name = serializers.SerializerMethodField(read_only=True)
    endpoint_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = SuiteCaseItem
        fields = [
            'id', 'suite', 'case_type', 'role',
            'case_api', 'case_ui',
            'order', 'enabled', 'env_override',
            'case_name', 'endpoint_name',
        ]
        extra_kwargs = {
            'suite': {'required': True},
            'case_api': {'required': False, 'allow_null': True},
            'case_ui': {'required': False, 'allow_null': True},
        }

    def get_case_name(self, obj):
        if obj.case_type == SuiteCaseItem.CaseType.API and obj.case_api:
            return obj.case_api.name
        if obj.case_type == SuiteCaseItem.CaseType.UI and obj.case_ui:
            return obj.case_ui.name
        return None

    def get_endpoint_name(self, obj):
        if obj.case_type == SuiteCaseItem.CaseType.API and obj.case_api:
            return obj.case_api.endpoint.name if hasattr(obj.case_api, 'endpoint') else None
        return None

    def validate(self, attrs):
        # PATCH 局部更新时跳过 case_type/case_api/case_ui 的关联校验
        if self.instance is not None and not attrs.get('case_type'):
            return attrs
        case_type = attrs.get('case_type', SuiteCaseItem.CaseType.API)
        if case_type == SuiteCaseItem.CaseType.API and not attrs.get('case_api'):
            raise serializers.ValidationError({'case_api': 'API 用例类型必须指定 case_api'})
        if case_type == SuiteCaseItem.CaseType.UI and not attrs.get('case_ui'):
            raise serializers.ValidationError({'case_ui': 'UI 用例类型必须指定 case_ui'})
        return attrs


class SuiteSerializer(serializers.ModelSerializer):
    """套件序列化器，包含用例项列表"""
    case_items = SuiteCaseItemSerializer(many=True, read_only=True, source='suite_case_items')
    case_api_count = serializers.SerializerMethodField(read_only=True)
    case_ui_count = serializers.SerializerMethodField(read_only=True)
    project_name = serializers.SerializerMethodField(read_only=True)
    environment_name = serializers.SerializerMethodField(read_only=True)
    updated_by_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Suite
        fields = [
            'id', 'name', 'description',
            'run_type', 'cron', 'hook_key',
            'project', 'project_name',
            'environment', 'environment_name',
            'suite_variables',
            'suite_headers',
            'timeout_seconds', 'fail_strategy', 'retry_count', 'retry_delay',
            'case_items', 'case_api_count', 'case_ui_count',
            'created_at', 'updated_by_name',
        ]

    def get_updated_by_name(self, obj):
        if obj.updated_by:
            return obj.updated_by.username
        if obj.created_by:
            return obj.created_by.username
        return None

    def get_case_api_count(self, obj):
        return obj.suite_case_items.filter(case_type=SuiteCaseItem.CaseType.API).count()

    def get_case_ui_count(self, obj):
        return obj.suite_case_items.filter(case_type=SuiteCaseItem.CaseType.UI).count()

    def get_project_name(self, obj):
        return obj.project.name if obj.project else None

    def get_environment_name(self, obj):
        return obj.environment.name if obj.environment else None


class RunResultSerializer(serializers.ModelSerializer):
    report_url = serializers.SerializerMethodField()
    log_url = serializers.SerializerMethodField()
    artifacts_url = serializers.SerializerMethodField()
    suite_name = serializers.SerializerMethodField()
    project_name = serializers.SerializerMethodField()

    class Meta:
        model = RunResult
        exclude = ["path"]

    def get_suite_name(self, obj):
        return obj.suite.name if obj.suite else None

    def get_project_name(self, obj):
        return obj.project.name if obj.project else None

    def get_report_url(self, obj):
        dir_name = Path(str(obj.path)).name
        return f"/api/suite/static/{dir_name}/report/index.html"

    def get_log_url(self, obj):
        dir_name = Path(str(obj.path)).name
        return f"/api/suite/static/{dir_name}/log/pytest.log"

    def get_artifacts_url(self, obj):
        dir_name = Path(str(obj.path)).name
        return f"/api/suite/static/{dir_name}/artifacts.zip"
