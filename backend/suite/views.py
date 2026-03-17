from pathlib import Path
from django.views.static import serve
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, permission_classes, api_view
from rest_framework.response import Response
from suite.serializers import SuiteSerializer, SuiteCaseItemSerializer, RunResultSerializer, EnvironmentSerializer, GlobalVariableSerializer, ServiceSerializer
from .models import Suite, SuiteCaseItem, RunResult, Environment, GlobalVariable, Service
from case_api.models import Case as CaseAPI
from case_ui.models import Case as CaseUI


@api_view()
@permission_classes([permissions.AllowAny])
def static_server(request, path, document_root=None, show_indexes=False):
    resp = serve(request, path, document_root, show_indexes)
    if resp.status_code == 200:
        if path.endswith(".yaml") or path.endswith(".log"):
            resp.headers["Content-Type"] = "text/css; charset=utf-8"
    return resp


@extend_schema(tags=["Suite"])
class SuiteViewSet(viewsets.ModelViewSet):
    serializer_class = SuiteSerializer
    queryset = Suite.objects.all().order_by('-id')
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get('project')
        if project_id:
            qs = qs.filter(project_id=project_id)
        run_type = self.request.query_params.get('run_type')
        if run_type:
            qs = qs.filter(run_type=run_type)
        search = self.request.query_params.get('search')
        if search:
            if search.isdigit():
                qs = qs.filter(id=int(search))
            else:
                qs = qs.filter(name__icontains=search)
        product_line_id = self.request.query_params.get('product_line')
        if product_line_id:
            qs = qs.filter(project__product_line_id=product_line_id)
        return qs

    @action(methods=['POST'], detail=True)
    def run(self, request, pk):
        """手动触发执行（所有类型套件均可手动触发）"""
        obj: Suite = self.get_object()
        initial_context = request.data.get("context") or {}
        result = obj.run(initial_context=initial_context)
        return Response({"result_id": result.id})

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(created_by=user, updated_by=user)

    def perform_update(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(updated_by=user)

    @action(methods=['POST'], detail=True)
    def webhook(self, request, pk):
        """Webhook 触发执行"""
        obj: Suite = self.get_object()
        hook_key = request.query_params.get('key')
        if obj.run_type != obj.RunType.WebHook:
            return Response(
                {"msg": f"本套件不允许 Webhook 触发，运行类型={obj.run_type}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if hook_key != obj.hook_key:
            return Response(
                {"msg": f"Webhook Key 不正确"},
                status=status.HTTP_400_BAD_REQUEST
            )
        initial_context = request.data.get("context") or {}
        result = obj.run(initial_context=initial_context)
        return Response({"result_id": result.id})

    @action(methods=['POST'], detail=True, url_path='stop_cron')
    def stop_cron(self, request, pk):
        """停止定时任务：清除关联的 django-q Schedule，并将套件改为手动执行"""
        obj: Suite = self.get_object()
        if obj.run_type != obj.RunType.CRON:
            return Response(
                {"msg": "该套件不是定时执行类型"},
                status=status.HTTP_400_BAD_REQUEST
            )
        # 删除 django-q 定时任务
        if obj.schedule:
            try:
                obj.schedule.delete()
            except Exception:
                pass
            obj.schedule = None
        obj.run_type = Suite.RunType.ONCE
        obj.cron = ''
        obj.save(update_fields=['run_type', 'cron', 'schedule'])
        return Response({"msg": "定时任务已停止，套件已切换为手动执行模式"})


@extend_schema(tags=["Suite"])
class SuiteCaseItemViewSet(viewsets.ModelViewSet):
    """
    套件用例项管理。

    支持操作：
    - GET    /api/suite/suite-case-item/?suite={id}   列出套件内所有用例项
    - POST   /api/suite/suite-case-item/              新增用例项
    - PATCH  /api/suite/suite-case-item/{id}/         修改（enabled/order/env_override）
    - DELETE /api/suite/suite-case-item/{id}/         删除
    - POST   /api/suite/suite-case-item/batch_add/    批量添加用例到套件
    - POST   /api/suite/suite-case-item/reorder/      批量更新排序
    """
    serializer_class = SuiteCaseItemSerializer
    queryset = SuiteCaseItem.objects.select_related(
        'case_api', 'case_api__endpoint', 'case_ui'
    ).order_by('order', 'id')
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        suite_id = self.request.query_params.get('suite')
        if suite_id:
            qs = qs.filter(suite_id=suite_id)
        case_type = self.request.query_params.get('case_type')
        if case_type:
            qs = qs.filter(case_type=case_type)
        return qs

    @action(methods=['POST'], detail=False)
    def batch_add(self, request):
        """
        批量添加用例到套件。

        请求体：
        {
            "suite": 1,
            "case_type": "API",          # API 或 UI
            "case_ids": [1, 2, 3]        # 用例 ID 列表
        }
        """
        suite_id = request.data.get('suite')
        case_type = request.data.get('case_type', SuiteCaseItem.CaseType.API)
        case_ids = request.data.get('case_ids', [])
        role = request.data.get('role', SuiteCaseItem.Role.MAIN)

        if not suite_id:
            return Response({'msg': 'suite 字段必填'}, status=status.HTTP_400_BAD_REQUEST)
        if not case_ids:
            return Response({'msg': 'case_ids 不能为空'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            suite = Suite.objects.get(id=suite_id)
        except Suite.DoesNotExist:
            return Response({'msg': '套件不存在'}, status=status.HTTP_404_NOT_FOUND)

        # 计算当前最大 order，新增项追加在末尾
        max_order = (
            suite.suite_case_items.order_by('-order').values_list('order', flat=True).first() or 0
        )

        created_items = []
        for i, cid in enumerate(case_ids, start=1):
            kwargs = {
                'suite': suite,
                'case_type': case_type,
                'role': role,
                'order': max_order + i,
                'enabled': True,
            }
            if case_type == SuiteCaseItem.CaseType.API:
                kwargs['case_api_id'] = cid
            else:
                kwargs['case_ui_id'] = cid
            item = SuiteCaseItem.objects.create(**kwargs)
            created_items.append(item)

        serializer = self.get_serializer(created_items, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=False)
    def reorder(self, request):
        """
        批量更新执行顺序。

        请求体：
        {
            "items": [
                {"id": 1, "order": 0},
                {"id": 2, "order": 1},
                ...
            ]
        }
        """
        items = request.data.get('items', [])
        if not items:
            return Response({'msg': 'items 不能为空'}, status=status.HTTP_400_BAD_REQUEST)

        updated = []
        for item in items:
            try:
                obj = SuiteCaseItem.objects.get(id=item['id'])
                obj.order = item['order']
                obj.save(update_fields=['order'])
                updated.append(obj.id)
            except (SuiteCaseItem.DoesNotExist, KeyError):
                pass

        return Response({'updated': updated})


@extend_schema(tags=["Suite"])
class RunResultViewSet(
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = RunResult.objects.select_related('suite', 'project').order_by('-id')
    serializer_class = RunResultSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        suite_id = self.request.query_params.get('suite')
        if suite_id:
            qs = qs.filter(suite_id=suite_id)
        search = self.request.query_params.get('search')
        if search:
            if search.isdigit():
                qs = qs.filter(id=int(search))
            else:
                qs = qs.filter(suite__name__icontains=search)
        is_pass = self.request.query_params.get('is_pass')
        if is_pass in ('true', 'false'):
            qs = qs.filter(is_pass=(is_pass == 'true'))
        product_line_id = self.request.query_params.get('product_line')
        if product_line_id:
            qs = qs.filter(suite__project__product_line_id=product_line_id)
        return qs


@extend_schema(tags=["Suite"])
class EnvironmentViewSet(viewsets.ModelViewSet):
    """运行环境 CRUD"""
    serializer_class = EnvironmentSerializer
    queryset = Environment.objects.select_related('project').order_by('-id')
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get('project')
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs


@extend_schema(tags=["Suite"])
class GlobalVariableViewSet(viewsets.ModelViewSet):
    """全局变量 CRUD"""
    serializer_class = GlobalVariableSerializer
    queryset = GlobalVariable.objects.select_related('environment').order_by('-id')
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        environment_id = self.request.query_params.get('environment')
        if environment_id:
            qs = qs.filter(environment_id=environment_id)
        return qs


@extend_schema(tags=["Suite"])
class ServiceViewSet(viewsets.ModelViewSet):
    """服务注册表 CRUD"""
    serializer_class = ServiceSerializer
    queryset = Service.objects.select_related('project').order_by('-id')
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get('project')
        if project_id:
            qs = qs.filter(project_id=project_id)
        product_line_id = self.request.query_params.get('product_line')
        if product_line_id:
            qs = qs.filter(project__product_line_id=product_line_id)
        return qs
