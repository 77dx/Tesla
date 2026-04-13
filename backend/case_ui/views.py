from drf_spectacular.utils import extend_schema
from django.conf import settings
from django.http import FileResponse, Http404
from pathlib import Path
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from product_line.models import ProductLineMember
from snippet.base_viewset import BaseViewSet
from suite.models import Environment, SuiteCaseItem

from .models import Element, Case, CaseRunHistory
from .runner import UICaseRunner
from .serializers import ElementSerializer, CaseUISerializer, CaseRunHistorySerializer


@extend_schema(tags=['Case_UI'])
class ElementViewSet(BaseViewSet):
    queryset = Element.objects.all().order_by('-id')
    serializer_class = ElementSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['name', 'id', 'value']
    product_line_field = 'project__product_line_id'


@extend_schema(tags=['Case_UI'])
class CaseViewSet(BaseViewSet):
    queryset = Case.objects.all().order_by('-id')
    serializer_class = CaseUISerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['name', 'id', 'entry_url']
    product_line_field = 'product_line_id'

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get('project')
        if project_id:
            qs = qs.filter(project_id=project_id)
        platform = self.request.query_params.get('platform')
        if platform:
            qs = qs.filter(platform=platform)
        return qs

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        refs = SuiteCaseItem.objects.filter(case_ui=instance).select_related('suite')
        if refs.exists():
            suite_names = '、'.join(set(r.suite.name for r in refs if r.suite))
            return Response({'message': f'该 UI 用例已被以下套件引用，无法删除：{suite_names}'}, status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        user = self.request.user
        project = serializer.validated_data.get('project')
        product_line = serializer.validated_data.get('product_line') or (project.product_line if project else None)
        if product_line and not (user.is_staff or user.is_superuser):
            if not ProductLineMember.objects.filter(user=user, product_line=product_line).exists():
                raise PermissionDenied('无该产品线权限')
        serializer.save(product_line=product_line, created_by=user if user.is_authenticated else None, updated_by=user if user.is_authenticated else None)

    def perform_update(self, serializer):
        user = self.request.user
        project = serializer.validated_data.get('project', serializer.instance.project)
        product_line = serializer.validated_data.get('product_line') or (project.product_line if project else serializer.instance.product_line)
        if product_line and not (user.is_staff or user.is_superuser):
            if not ProductLineMember.objects.filter(user=user, product_line=product_line).exists():
                raise PermissionDenied('无该产品线权限')
        serializer.save(product_line=product_line, updated_by=user if user.is_authenticated else None)

    @action(methods=['GET'], detail=True)
    def history(self, request, *args, **kwargs):
        case = self.get_object()
        qs = CaseRunHistory.objects.filter(case=case).select_related('environment', 'created_by').order_by('-id')[:20]
        serializer = CaseRunHistorySerializer(qs, many=True)
        return Response({'result': serializer.data})

    @action(methods=['GET'], detail=True, url_path=r'history/(?P<history_id>[^/.]+)/screenshot')
    def history_screenshot(self, request, *args, **kwargs):
        case = self.get_object()
        history_id = kwargs.get('history_id')
        index = int(request.query_params.get('index', 0))
        history = CaseRunHistory.objects.filter(case=case, id=history_id).first()
        if not history:
            raise Http404('历史记录不存在')
        shots = history.screenshots or []
        if index < 0 or index >= len(shots):
            raise Http404('截图不存在')
        shot_path = Path(shots[index]).resolve()
        base_dir = (Path(settings.BASE_DIR) / 'ui_case_runs').resolve()
        if not str(shot_path).startswith(str(base_dir)) or not shot_path.exists() or not shot_path.is_file():
            raise Http404('截图文件不存在')
        return FileResponse(open(shot_path, 'rb'), content_type='image/png')

    @action(methods=['POST'], detail=True)
    def run(self, request, *args, **kwargs):
        case = self.get_object()
        environment = None
        environment_id = request.data.get('environment')
        if environment_id:
            try:
                environment = Environment.objects.get(id=environment_id)
            except Environment.DoesNotExist:
                return Response({'message': '环境不存在'}, status=status.HTTP_404_NOT_FOUND)

        result_dir = None
        try:
            from pathlib import Path
            from django.conf import settings
            result_dir = Path(settings.BASE_DIR) / 'ui_case_runs' / f'case_{case.id}'
            result_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            result_dir = None

        from case_api.engine import ContextStore
        ctx = ContextStore(backend='memory')
        runner = UICaseRunner(ctx=ctx, environment=environment, result_dir=result_dir)
        case_result = runner.run_case(case)
        history = CaseRunHistory.objects.create(
            case=case,
            environment=environment,
            success=case_result.success,
            error=case_result.error,
            duration=case_result.duration,
            retry_count=case_result.retry_count,
            assertions=case_result.assertions,
            extracted=case_result.extracted,
            screenshots=case_result.screenshots,
            execution_logs=case_result.execution_logs,
            created_by=request.user if request.user.is_authenticated else None,
        )
        payload = case_result.to_dict()
        payload['history_id'] = history.id
        return Response({'message': '执行完成', 'result': payload})
