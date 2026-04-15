from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions
from .models import (
    Project, Config, Sprint, Requirement,
    ProjectCaseRef, ProjectSuiteRef, SprintCaseRef, SprintSuiteRef,
)
from .serializers import (
    ProjectSerializer, ConfigSerializer, SprintSerializer, RequirementSerializer,
    ProjectCaseRefSerializer, ProjectSuiteRefSerializer, SprintCaseRefSerializer, SprintSuiteRefSerializer,
)
from snippet.base_viewset import BaseViewSet
from snippet.permissions import has_permission
from product_line.models import ProductLineMember
from rest_framework.exceptions import PermissionDenied
# from suite.models import Suite


def _assert_product_line_member(user, product_line_id):
    if not product_line_id:
        return
    if user.is_staff or user.is_superuser:
        return
    if not ProductLineMember.objects.filter(user=user, product_line_id=product_line_id).exists():
        raise PermissionDenied('无该产品线权限')


def _assert_can_access_resource(user, product_line_id):
    if not product_line_id:
        return
    _assert_product_line_member(user, product_line_id)


@extend_schema(tags=["Project"])
class ProjectViewSet(BaseViewSet):
    queryset = Project.objects.all().order_by('-id')
    serializer_class = ProjectSerializer
    search_fields = ['name', 'id']
    product_line_field = 'product_line_id'

    def get_queryset(self):
        qs = super().get_queryset()
        status = self.request.query_params.get('status')
        if status:
            qs = qs.filter(status=status)
        pm_id = self.request.query_params.get('pm')
        if pm_id:
            qs = qs.filter(pm_id=pm_id)
        return qs

    @action(methods=['POST'], detail=True, url_path='run')
    def run_project(self, request, pk=None):
        project = self.get_object()
        _assert_product_line_member(request.user, project.product_line_id)
        if not has_permission(request.user, 'project:run'):
            raise PermissionDenied('无执行项目测试权限')
        suite_ids = request.data.get('suite_ids') or []
        qs = project.suite_refs.select_related('suite').filter(enabled=True)
        if suite_ids:
            qs = qs.filter(suite_id__in=suite_ids)

        result_ids = []
        for ref in qs:
            suite = ref.suite
            if not suite:
                continue
            result = suite.run(
                scope_type='project',
                scope_id=project.id,
                trigger_source='manual',
                initial_context=request.data.get('context') or {},
                dataset_id=request.data.get('dataset_id') or None,
                product_line=project.product_line,
            )
            result_ids.append(result.id)
        return Response({'result_ids': result_ids})


@extend_schema(tags=["Project"])
class ConfigViewSet(BaseViewSet):
    queryset = Config.objects.all().order_by('-id')
    serializer_class = ConfigSerializer
    product_line_field = None


@extend_schema(tags=["Sprint"])
class SprintViewSet(BaseViewSet):
    """迭代 CRUD，支持按 project / product_line 过滤"""
    queryset = Sprint.objects.select_related('project', 'product_line', 'created_by', 'updated_by').order_by('-start_date', '-id')
    serializer_class = SprintSerializer
    search_fields = ['name', 'goal']
    product_line_field = 'product_line_id'

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get('project')
        if project_id:
            qs = qs.filter(project_id=project_id)
        status = self.request.query_params.get('status')
        if status:
            qs = qs.filter(status=status)
        owner_id = self.request.query_params.get('owner')
        if owner_id:
            qs = qs.filter(owner_id=owner_id)
        return qs

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        project = serializer.validated_data.get('project')
        product_line = serializer.validated_data.get('product_line')
        pl_id = (product_line.id if product_line else None)
        if not pl_id and project:
            pl_id = project.product_line_id
        _assert_product_line_member(self.request.user, pl_id)
        owner = serializer.validated_data.get('owner') or user
        serializer.save(created_by=user, updated_by=user, owner=owner, product_line_id=pl_id)

    def perform_update(self, serializer):
        project = serializer.validated_data.get('project') or getattr(serializer.instance, 'project', None)
        product_line = serializer.validated_data.get('product_line') or getattr(serializer.instance, 'product_line', None)
        pl_id = (product_line.id if product_line else None)
        if not pl_id and project:
            pl_id = project.product_line_id
        _assert_product_line_member(self.request.user, pl_id)
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(product_line_id=pl_id, updated_by=user)

    @action(methods=['POST'], detail=True, url_path='run')
    def run_sprint(self, request, pk=None):
        sprint = self.get_object()
        pl_id = sprint.product_line_id or (sprint.project.product_line_id if sprint.project else None)
        _assert_product_line_member(request.user, pl_id)
        if not has_permission(request.user, 'sprint:run'):
            raise PermissionDenied('无执行迭代测试权限')
        suite_ids = request.data.get('suite_ids') or []
        qs = sprint.suite_refs.select_related('suite').filter(enabled=True)
        if suite_ids:
            qs = qs.filter(suite_id__in=suite_ids)

        result_ids = []
        for ref in qs:
            suite = ref.suite
            if not suite:
                continue
            result = suite.run(
                scope_type='sprint',
                scope_id=sprint.id,
                trigger_source='manual',
                initial_context=request.data.get('context') or {},
                dataset_id=request.data.get('dataset_id') or None,
                product_line=sprint.product_line or (sprint.project.product_line if sprint.project else None),
            )
            result_ids.append(result.id)
        return Response({'result_ids': result_ids})

    @action(methods=['GET'], detail=True, url_path='requirements')
    def requirements(self, request, pk=None):
        """获取某迭代下所有需求"""
        sprint = self.get_object()
        reqs = sprint.requirements.select_related('assignee', 'created_by').order_by('-priority', 'due_date')
        return Response(RequirementSerializer(reqs, many=True).data)


@extend_schema(tags=["Requirement"])
class RequirementViewSet(BaseViewSet):
    """需求 CRUD，支持按 sprint / project 过滤"""
    queryset = Requirement.objects.select_related(
        'sprint__project', 'assignee', 'created_by'
    ).order_by('-priority', 'due_date', '-id')
    serializer_class = RequirementSerializer
    search_fields = ['title', 'desc']
    product_line_field = 'sprint__product_line_id'

    def get_queryset(self):
        qs = super().get_queryset()
        sprint_id = self.request.query_params.get('sprint')
        if sprint_id:
            qs = qs.filter(sprint_id=sprint_id)
        project_id = self.request.query_params.get('project')
        if project_id:
            qs = qs.filter(sprint__project_id=project_id)
        status = self.request.query_params.get('status')
        if status:
            qs = qs.filter(status=status)
        assignee_id = self.request.query_params.get('assignee')
        if assignee_id:
            qs = qs.filter(assignee_id=assignee_id)
        return qs

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(created_by=user)


@extend_schema(tags=["ProjectRef"])
class ProjectCaseRefViewSet(BaseViewSet):
    queryset = ProjectCaseRef.objects.select_related('project', 'case').order_by('-id')
    serializer_class = ProjectCaseRefSerializer
    permission_classes = [permissions.IsAuthenticated]
    product_line_field = 'project__product_line_id'

    def perform_create(self, serializer):
        user = self.request.user
        project = serializer.validated_data['project']
        case = serializer.validated_data['case']
        _assert_product_line_member(user, project.product_line_id)
        if not has_permission(user, 'project:ref_case'):
            raise PermissionDenied('无项目引用用例权限')
        _assert_can_access_resource(user, case.product_line_id)
        serializer.save(created_by=user)


@extend_schema(tags=["ProjectRef"])
class ProjectSuiteRefViewSet(BaseViewSet):
    queryset = ProjectSuiteRef.objects.select_related('project', 'suite').order_by('-id')
    serializer_class = ProjectSuiteRefSerializer
    permission_classes = [permissions.IsAuthenticated]
    product_line_field = 'project__product_line_id'

    def perform_create(self, serializer):
        user = self.request.user
        project = serializer.validated_data['project']
        suite = serializer.validated_data['suite']
        _assert_product_line_member(user, project.product_line_id)
        if not has_permission(user, 'project:ref_suite'):
            raise PermissionDenied('无项目引用套件权限')
        _assert_can_access_resource(user, suite.product_line_id)
        serializer.save(created_by=user)


@extend_schema(tags=["ProjectRef"])
class SprintCaseRefViewSet(BaseViewSet):
    queryset = SprintCaseRef.objects.select_related('sprint__product_line', 'case').order_by('-id')
    serializer_class = SprintCaseRefSerializer
    permission_classes = [permissions.IsAuthenticated]
    product_line_field = 'sprint__product_line_id'

    def perform_create(self, serializer):
        user = self.request.user
        sprint = serializer.validated_data['sprint']
        case = serializer.validated_data['case']
        pl_id = sprint.product_line_id or (sprint.project.product_line_id if sprint.project else None)
        _assert_product_line_member(user, pl_id)
        if not has_permission(user, 'sprint:ref_case'):
            raise PermissionDenied('无迭代引用用例权限')
        _assert_can_access_resource(user, case.product_line_id)
        serializer.save(created_by=user)


@extend_schema(tags=["ProjectRef"])
class SprintSuiteRefViewSet(BaseViewSet):
    queryset = SprintSuiteRef.objects.select_related('sprint__product_line', 'suite').order_by('-id')
    serializer_class = SprintSuiteRefSerializer
    permission_classes = [permissions.IsAuthenticated]
    product_line_field = 'sprint__product_line_id'

    def perform_create(self, serializer):
        user = self.request.user
        sprint = serializer.validated_data['sprint']
        suite = serializer.validated_data['suite']
        pl_id = sprint.product_line_id or (sprint.project.product_line_id if sprint.project else None)
        _assert_product_line_member(user, pl_id)
        if not has_permission(user, 'sprint:ref_suite'):
            raise PermissionDenied('无迭代引用套件权限')
        _assert_can_access_resource(user, suite.product_line_id)
        serializer.save(created_by=user)


