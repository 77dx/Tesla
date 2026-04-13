from pathlib import Path

from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from product_line.models import ProductLineMember
from snippet.base_viewset import BaseViewSet

from .models import AutomationProject, AutomationSuite, AutomationRun
from .serializers import AutomationProjectSerializer, AutomationSuiteSerializer, AutomationRunSerializer
from .tasks import run_automation_task


@extend_schema(tags=['Automation'])
class AutomationProjectViewSet(BaseViewSet):
    queryset = AutomationProject.objects.select_related('product_line', 'project').order_by('-id')
    serializer_class = AutomationProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['name', 'id', 'repo_url', 'local_repo_path']
    product_line_field = 'product_line_id'

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return qs
        allowed = ProductLineMember.objects.filter(user=user).values_list('product_line_id', flat=True)
        return qs.filter(product_line_id__in=allowed)


@extend_schema(tags=['Automation'])
class AutomationSuiteViewSet(BaseViewSet):
    queryset = AutomationSuite.objects.select_related('automation_project__product_line').order_by('-id')
    serializer_class = AutomationSuiteSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['name', 'suite_path', 'id']
    product_line_field = 'automation_project__product_line_id'

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if not (user.is_staff or user.is_superuser):
            allowed = ProductLineMember.objects.filter(user=user).values_list('product_line_id', flat=True)
            qs = qs.filter(automation_project__product_line_id__in=allowed)
        automation_project_id = self.request.query_params.get('automation_project')
        if automation_project_id:
            qs = qs.filter(automation_project_id=automation_project_id)
        return qs

    @action(methods=['post'], detail=True)
    def run(self, request, pk=None):
        suite = self.get_object()
        project = suite.automation_project
        env_id = request.data.get('environment')
        environment = None
        if env_id:
            from suite.models import Environment
            environment = Environment.objects.filter(id=env_id).first()

        command = (request.data.get('command') or '').strip() or suite.command_override or project.test_command
        if suite.suite_path and not suite.command_override and command == project.test_command:
            command = f"{command} {suite.suite_path}".strip()

        base_url = request.data.get('base_url') or (environment.base_url if environment else '')
        variables = request.data.get('variables') or (environment.variables if environment and environment.variables else {})
        branch = request.data.get('branch') or project.default_branch

        run = AutomationRun.objects.create(
            suite=suite,
            product_line=project.product_line,
            project=project.project,
            environment=environment,
            trigger_source='manual',
            branch=branch,
            command=command,
            base_url=base_url or '',
            variables=variables or {},
            created_by=request.user if request.user.is_authenticated else None,
        )
        run_automation_task.delay(run.id)
        return Response({'run_id': run.id}, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Automation'])
class AutomationRunViewSet(BaseViewSet):
    queryset = AutomationRun.objects.select_related('suite__automation_project', 'product_line', 'project', 'environment').order_by('-id')
    serializer_class = AutomationRunSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['id', 'branch', 'command']
    product_line_field = 'product_line_id'

    @action(methods=['get'], detail=True)
    def log_preview(self, request, pk=None):
        run = self.get_object()
        if not run.log_path:
            return Response({'content': ''})
        log_path = Path(run.log_path)
        if not log_path.exists():
            return Response({'content': ''})
        try:
            content = log_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as exc:
            return Response({'content': '', 'error': str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'content': content[-12000:]})

    @action(methods=['get'], detail=True)
    def report_meta(self, request, pk=None):
        run = self.get_object()
        report_url = ''
        if run.report_path:
            report_index = Path(run.report_path) / 'index.html'
            if report_index.exists():
                try:
                    report_url = '/reports/' + str(report_index.relative_to(Path(settings.REPORT_DIR))).replace('\\', '/')
                except Exception:
                    report_url = ''
        return Response({'report_url': report_url})

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if not (user.is_staff or user.is_superuser):
            allowed = ProductLineMember.objects.filter(user=user).values_list('product_line_id', flat=True)
            qs = qs.filter(product_line_id__in=allowed)
        suite_id = self.request.query_params.get('suite')
        if suite_id:
            qs = qs.filter(suite_id=suite_id)
        status_value = self.request.query_params.get('status')
        if status_value:
            qs = qs.filter(status=status_value)
        return qs
