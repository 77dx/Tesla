"""
套件序列化器
"""
from pathlib import Path
from rest_framework import serializers
from case_api.models import Case as CaseAPI
from case_ui.models import Case as CaseUI
from .models import (
    Suite, SuiteCaseItem, RunResult, Environment, GlobalVariable, Service, DataSet,
    ExecutionSnapshot, ExecutionCaseSnapshot, ImportJob, SuiteExecutionLog,
    SuiteNode,
)


class ServiceSerializer(serializers.ModelSerializer):
    project_name = serializers.SerializerMethodField(read_only=True)
    product_line_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Service
        fields = ['id', 'key', 'name', 'description', 'project', 'project_name', 'product_line_name', 'created_at']

    def get_project_name(self, obj):
        return obj.project.name if obj.project else None

    def get_product_line_name(self, obj):
        if obj.project and obj.project.product_line:
            return obj.project.product_line.name
        return None


class EnvironmentSerializer(serializers.ModelSerializer):
    project_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Environment
        fields = ['id', 'name', 'project', 'project_name', 'base_url', 'urls',
                  'headers', 'variables', 'mock_rules', 'description', 'created_at']

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
    product_line_name = serializers.CharField(source='product_line.name', read_only=True)
    environment_name = serializers.SerializerMethodField(read_only=True)
    updated_by_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Suite
        fields = [
            'id', 'name', 'description',
            'run_type', 'cron', 'cron_next_run_at', 'hook_key',
            'project', 'project_name',
            'product_line', 'product_line_name',
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

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class SuiteNodeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    item = serializers.SerializerMethodField()

    class Meta:
        model = SuiteNode
        fields = ['id', 'name', 'parent', 'path', 'node_type', 'suite', 'order_no', 'children', 'item']

    def get_children(self, obj):
        children = obj.children.all().order_by('order_no', 'id')
        return SuiteNodeSerializer(children, many=True).data

    def get_item(self, obj):
        if obj.node_type == SuiteNode.NodeType.SUITE and obj.suite:
            return {'id': obj.suite.id, 'name': obj.suite.name}
        return None


class RunResultSerializer(serializers.ModelSerializer):
    report_url = serializers.SerializerMethodField()
    log_url = serializers.SerializerMethodField()
    artifacts_url = serializers.SerializerMethodField()
    suite_name = serializers.SerializerMethodField()
    project_name = serializers.SerializerMethodField()
    scope_name = serializers.SerializerMethodField()

    class Meta:
        model = RunResult
        exclude = ["path"]

    def get_suite_name(self, obj):
        return obj.suite.name if obj.suite else None

    def get_project_name(self, obj):
        return obj.project.name if obj.project else None

    def get_scope_name(self, obj):
        if obj.scope_type == 'project':
            return obj.project.name if obj.project else '无'
        if obj.scope_type == 'sprint':
            from project.models import Sprint
            sprint = Sprint.objects.filter(id=obj.scope_id).first()
            return sprint.name if sprint else f'迭代 #{obj.scope_id}'
        return '无'

    def get_report_url(self, obj):
        dir_name = Path(str(obj.path)).name
        return f"/api/suite/static/{dir_name}/report/index.html"

    def get_log_url(self, obj):
        dir_name = Path(str(obj.path)).name
        return f"/api/suite/static/{dir_name}/log/pytest.log"

    def get_artifacts_url(self, obj):
        dir_name = Path(str(obj.path)).name
        return f"/api/suite/static/{dir_name}/artifacts.zip"


class SuiteExecutionLogSerializer(serializers.ModelSerializer):
    latest_result = RunResultSerializer(read_only=True)
    latest_failed_result = RunResultSerializer(read_only=True)
    recent_results = serializers.SerializerMethodField()
    pass_rate = serializers.SerializerMethodField()
    failure_summary = serializers.SerializerMethodField()

    class Meta:
        model = SuiteExecutionLog
        fields = [
            'id', 'suite', 'strategy_type', 'strategy_key', 'strategy_label', 'strategy_payload',
            'execution_count', 'pass_count', 'fail_count', 'pass_rate', 'failure_summary',
            'latest_result', 'latest_failed_result', 'recent_result_ids', 'recent_results',
            'first_triggered_at', 'last_triggered_at', 'created_at', 'updated_at',
        ]

    def get_recent_results(self, obj):
        ids = obj.recent_result_ids or []
        if not ids:
            return []
        result_map = {r.id: r for r in RunResult.objects.filter(id__in=ids).select_related('suite', 'project')}
        ordered = [result_map[rid] for rid in ids if rid in result_map]
        return RunResultSerializer(ordered, many=True, context=self.context).data

    def get_pass_rate(self, obj):
        total = obj.execution_count or 0
        if total <= 0:
            return 0
        return round((obj.pass_count or 0) * 100 / total, 2)

    def get_failure_summary(self, obj):
        result = obj.latest_failed_result
        if not result or not result.path:
            return ''
        log_path = Path(str(result.path)) / 'log' / 'pytest.log'
        if not log_path.exists():
            return ''
        try:
            content = log_path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return ''
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        for line in reversed(lines):
            upper = line.upper()
            if 'ASSERT' in upper or 'ERROR' in upper or 'FAILED' in upper or 'EXCEPTION' in upper:
                return line[:300]
        return lines[-1][:300] if lines else ''


class DataSetSerializer(serializers.ModelSerializer):
    row_count       = serializers.SerializerMethodField(read_only=True)
    project_name    = serializers.SerializerMethodField(read_only=True)
    created_by_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model  = DataSet
        fields = [
            'id', 'name', 'project', 'project_name',
            'columns', 'rows', 'row_count',
            'created_by', 'created_by_name',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_row_count(self, obj):
        return len(obj.rows) if obj.rows else 0

    def get_project_name(self, obj):
        return obj.project.name if obj.project else None

    def get_created_by_name(self, obj):
        return obj.created_by.username if obj.created_by else None


class ExecutionCaseSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExecutionCaseSnapshot
        fields = '__all__'


class ExecutionSnapshotSerializer(serializers.ModelSerializer):
    case_snapshots = ExecutionCaseSnapshotSerializer(many=True, read_only=True)

    class Meta:
        model = ExecutionSnapshot
        fields = '__all__'


class ImportJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportJob
        fields = '__all__'
