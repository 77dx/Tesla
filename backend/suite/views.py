from pathlib import Path
from django.db import transaction
from django.db.models import Q
from django.views.static import serve
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, permission_classes, api_view
from rest_framework.response import Response
from suite.serializers import (
    SuiteSerializer, SuiteCaseItemSerializer, RunResultSerializer, SuiteExecutionLogSerializer,
    EnvironmentSerializer, GlobalVariableSerializer, ServiceSerializer, DataSetSerializer,
    ExecutionSnapshotSerializer, ImportJobSerializer, SuiteNodeSerializer,
)
from .models import (
    Suite, SuiteCaseItem, RunResult, Environment, GlobalVariable, Service, DataSet,
    ExecutionSnapshot, ImportJob, SuiteNode, SuiteExecutionLog,
)
from case_api.models import Case as CaseAPI
from case_ui.models import Case as CaseUI
from product_line.models import ProductLineMember


@api_view()
@permission_classes([permissions.AllowAny])
def static_server(request, path, document_root=None, show_indexes=False):
    resp = serve(request, path, document_root, show_indexes)
    if resp.status_code == 200:
        if path.endswith(".yaml") or path.endswith(".log"):
            resp.headers["Content-Type"] = "text/css; charset=utf-8"
    return resp


from snippet.base_viewset import BaseViewSet


@extend_schema(tags=["Suite"])
class SuiteViewSet(BaseViewSet):
    serializer_class = SuiteSerializer
    queryset = Suite.objects.all().order_by('-id')
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['name', 'id']
    product_line_field = None

    def get_queryset(self):
        qs = super().get_queryset()
        run_type = self.request.query_params.get('run_type')
        if run_type:
            qs = qs.filter(run_type=run_type)
        product_line_id = self.request.query_params.get('product_line')
        if product_line_id:
            qs = qs.filter(product_line_id=product_line_id)
        return qs

    @action(methods=['POST'], detail=True)
    def run(self, request, pk):
        """手动触发执行（所有类型套件均可手动触发）"""
        obj: Suite = self.get_object()
        initial_context = request.data.get("context") or {}
        dataset_id = request.data.get("dataset_id") or None
        scope_type = request.data.get('scope_type') or RunResult.ScopeType.PROJECT
        scope_id = request.data.get('scope_id')
        if scope_id is None:
            scope_id = obj.project_id if obj.project_id else 0

        pl_id = obj.product_line_id or (obj.project.product_line_id if obj.project else None)
        if pl_id and not (request.user.is_staff or request.user.is_superuser):
            if not ProductLineMember.objects.filter(user=request.user, product_line_id=pl_id).exists():
                return Response({'detail': '无该产品线权限'}, status=status.HTTP_403_FORBIDDEN)

        result = obj.run(
            initial_context=initial_context,
            dataset_id=dataset_id,
            scope_type=scope_type,
            scope_id=int(scope_id) if scope_id not in (None, '') else 0,
            trigger_source='manual',
        )
        return Response({"result_id": result.id})

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        obj = serializer.save(created_by=user, updated_by=user, project=None, product_line=None)
        root = SuiteNode.ensure_root()
        parent_id = self.request.data.get('parent_node_id')
        parent = SuiteNode.objects.filter(id=parent_id, node_type=SuiteNode.NodeType.FOLDER).first() if parent_id else root
        if not hasattr(obj, 'tree_node'):
            node = SuiteNode.objects.create(name=obj.name, parent=parent, node_type=SuiteNode.NodeType.SUITE, suite=obj)
            node.path = f"{parent.path}{node.id}/"
            node.save(update_fields=['path'])

    def perform_update(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(updated_by=user, project=None, product_line=None)

    @action(methods=['POST'], detail=True, url_path='stop_cron')
    def stop_cron(self, request, pk):
        """停止定时任务：清除 cron 配置，并将套件改为手动执行"""
        obj: Suite = self.get_object()
        if obj.run_type != obj.RunType.CRON:
            return Response(
                {"msg": "该套件不是定时执行类型"},
                status=status.HTTP_400_BAD_REQUEST
            )
        obj.run_type = Suite.RunType.ONCE
        obj.cron = ''
        obj.cron_next_run_at = None
        obj.save(update_fields=['run_type', 'cron', 'cron_next_run_at'])
        return Response({"msg": "定时任务已停止，套件已切换为手动执行模式"})


@extend_schema(tags=["Suite"])
class SuiteNodeViewSet(viewsets.GenericViewSet):
    queryset = SuiteNode.objects.all().order_by('order_no', 'id')
    serializer_class = SuiteNodeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def _can_manage_tree(self, user):
        return user.is_authenticated

    def destroy(self, request, *args, **kwargs):
        """
        删除目录节点：
        - 仅当该节点下没有任何子节点时允许删除
        - 套件节点不允许通过该接口删除（请在套件列表中删除）
        """
        if not self._can_manage_tree(request.user):
            return Response({'message': '无目录管理权限'}, status=status.HTTP_403_FORBIDDEN)
        node = self.get_object()
        if node.node_type == SuiteNode.NodeType.SUITE:
            return Response({'message': '套件节点请在套件列表中删除'}, status=status.HTTP_400_BAD_REQUEST)
        if node.children.exists():
            return Response({'message': '该节点下仍有子节点，无法删除'}, status=status.HTTP_400_BAD_REQUEST)
        node.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def list(self, request):
        root = SuiteNode.ensure_root()
        for s in Suite.objects.filter(tree_node__isnull=True):
            node = SuiteNode.objects.create(name=s.name, parent=root, node_type=SuiteNode.NodeType.SUITE, suite=s)
            node.path = f"{root.path}{node.id}/"
            node.save(update_fields=['path'])
        root = SuiteNode.objects.get(id=root.id)
        data = self.get_serializer(root).data
        pl_id = request.query_params.get('product_line')
        if pl_id:
            def filter_node(node):
                if node.get('node_type') == 'suite':
                    suite_obj = node.get('item') or {}
                    suite_id = suite_obj.get('id')
                    if not suite_id:
                        return None
                    suite = Suite.objects.filter(id=suite_id).only('product_line_id').first()
                    return node if suite and str(suite.product_line_id or '') == str(pl_id) else None
                children = []
                for child in node.get('children') or []:
                    filtered = filter_node(child)
                    if filtered:
                        children.append(filtered)
                node['children'] = children
                return node if node.get('parent') is None or children else None
            data = filter_node(data) or data
        return Response(data)

    @action(methods=['POST'], detail=False)
    def create_folder(self, request):
        if not self._can_manage_tree(request.user):
            return Response({'message': '无目录管理权限'}, status=status.HTTP_403_FORBIDDEN)
        name = (request.data.get('name') or '').strip()
        parent_id = request.data.get('parent_id')
        if not name:
            return Response({'message': 'name 必填'}, status=status.HTTP_400_BAD_REQUEST)
        parent = SuiteNode.objects.filter(id=parent_id).first() if parent_id else SuiteNode.ensure_root()
        if not parent:
            return Response({'message': '父节点不存在'}, status=status.HTTP_404_NOT_FOUND)
        if parent.node_type != SuiteNode.NodeType.FOLDER:
            return Response({'message': '仅可在文件夹下创建'}, status=status.HTTP_400_BAD_REQUEST)
        node = SuiteNode.objects.create(name=name, parent=parent, node_type=SuiteNode.NodeType.FOLDER)
        node.path = f"{parent.path}{node.id}/"
        node.save(update_fields=['path'])
        return Response(self.get_serializer(node).data, status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=False)
    def attach_suite(self, request):
        if not self._can_manage_tree(request.user):
            return Response({'message': '无目录管理权限'}, status=status.HTTP_403_FORBIDDEN)
        suite_id = request.data.get('suite_id')
        parent_id = request.data.get('parent_id')
        if not suite_id:
            return Response({'message': 'suite_id 必填'}, status=status.HTTP_400_BAD_REQUEST)
        suite_obj = Suite.objects.filter(id=suite_id).first()
        if not suite_obj:
            return Response({'message': '套件不存在'}, status=status.HTTP_404_NOT_FOUND)
        parent = SuiteNode.objects.filter(id=parent_id).first() if parent_id else SuiteNode.ensure_root()
        if not parent or parent.node_type != SuiteNode.NodeType.FOLDER:
            return Response({'message': '目标文件夹不存在'}, status=status.HTTP_400_BAD_REQUEST)

        node = SuiteNode.objects.filter(suite=suite_obj).first()
        if node:
            old_path = node.path
            new_path = f"{parent.path}{node.id}/"
            with transaction.atomic():
                node.parent = parent
                node.name = suite_obj.name
                node.path = new_path
                node.save(update_fields=['parent', 'name', 'path'])
                descendants = SuiteNode.objects.filter(path__startswith=old_path).exclude(id=node.id)
                for child in descendants:
                    child.path = child.path.replace(old_path, new_path, 1)
                    child.save(update_fields=['path'])
        else:
            node = SuiteNode.objects.create(name=suite_obj.name, parent=parent, node_type=SuiteNode.NodeType.SUITE, suite=suite_obj)
            node.path = f"{parent.path}{node.id}/"
            node.save(update_fields=['path'])
        return Response(self.get_serializer(node).data)

    @action(methods=['POST'], detail=False)
    def rename(self, request):
        if not self._can_manage_tree(request.user):
            return Response({'message': '无目录管理权限'}, status=status.HTTP_403_FORBIDDEN)
        node_id = request.data.get('node_id')
        name = (request.data.get('name') or '').strip()
        if not name:
            return Response({'message': 'name 必填'}, status=status.HTTP_400_BAD_REQUEST)
        node = SuiteNode.objects.filter(id=node_id).first() if node_id else SuiteNode.ensure_root()
        if not node:
            return Response({'message': '节点不存在'}, status=status.HTTP_404_NOT_FOUND)
        node.name = name
        node.save(update_fields=['name'])
        if node.node_type == SuiteNode.NodeType.SUITE and node.suite:
            node.suite.name = name
            node.suite.save(update_fields=['name'])
        return Response(self.get_serializer(node).data)

    @action(methods=['POST'], detail=False)
    def move(self, request):
        if not self._can_manage_tree(request.user):
            return Response({'message': '无目录管理权限'}, status=status.HTTP_403_FORBIDDEN)
        node_id = request.data.get('node_id')
        target_parent_id = request.data.get('target_parent_id')
        node = SuiteNode.objects.filter(id=node_id).first()
        target_parent = SuiteNode.objects.filter(id=target_parent_id).first()
        if not node or not target_parent:
            return Response({'message': '节点不存在'}, status=status.HTTP_404_NOT_FOUND)
        if target_parent.node_type != SuiteNode.NodeType.FOLDER:
            return Response({'message': '仅可移动到文件夹'}, status=status.HTTP_400_BAD_REQUEST)
        if node.id == target_parent.id or target_parent.path.startswith(node.path):
            return Response({'message': '不能移动到自身或子节点下'}, status=status.HTTP_400_BAD_REQUEST)

        old_path = node.path
        new_path = f"{target_parent.path}{node.id}/"
        with transaction.atomic():
            node.parent = target_parent
            node.path = new_path
            node.save(update_fields=['parent', 'path'])
            descendants = SuiteNode.objects.filter(path__startswith=old_path).exclude(id=node.id)
            for child in descendants:
                child.path = child.path.replace(old_path, new_path, 1)
                child.save(update_fields=['path'])
        return Response(self.get_serializer(node).data)


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
    permission_classes = [permissions.IsAuthenticated]

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
class SuiteExecutionLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SuiteExecutionLog.objects.select_related('suite', 'latest_result').order_by('-last_triggered_at', '-id')
    serializer_class = SuiteExecutionLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if not (user.is_staff or user.is_superuser):
            allowed_pl_ids = ProductLineMember.objects.filter(user=user).values_list('product_line_id', flat=True)
            qs = qs.filter(suite__product_line_id__in=allowed_pl_ids)

        suite_id = self.request.query_params.get('suite')
        if suite_id:
            qs = qs.filter(suite_id=suite_id)
        strategy_type = self.request.query_params.get('strategy_type')
        if strategy_type:
            qs = qs.filter(strategy_type=strategy_type)
        return qs


@extend_schema(tags=["Suite"])
class RunResultViewSet(
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = RunResult.objects.select_related('suite', 'project', 'product_line').order_by('-id')
    serializer_class = RunResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if not (user.is_staff or user.is_superuser):
            allowed_pl_ids = ProductLineMember.objects.filter(user=user).values_list('product_line_id', flat=True)
            qs = qs.filter(product_line_id__in=allowed_pl_ids)

        suite_id = self.request.query_params.get('suite')
        if suite_id:
            qs = qs.filter(suite_id=suite_id)
        execution_log_id = self.request.query_params.get('execution_log')
        if execution_log_id:
            qs = qs.filter(execution_log_id=execution_log_id)

        scope_type = self.request.query_params.get('scope_type')
        scope_id = self.request.query_params.get('scope_id')
        if scope_type:
            qs = qs.filter(scope_type=scope_type)
        if scope_id:
            qs = qs.filter(scope_id=scope_id)

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
            qs = qs.filter(
                Q(product_line_id=product_line_id) |
                (Q(product_line__isnull=True) & Q(suite__product_line_id=product_line_id)) |
                (Q(product_line__isnull=True) & Q(project__product_line_id=product_line_id))
            )
        return qs


@extend_schema(tags=["Suite"])
class EnvironmentViewSet(viewsets.ModelViewSet):
    """运行环境 CRUD"""
    serializer_class = EnvironmentSerializer
    queryset = Environment.objects.select_related('project').order_by('-id')
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get('project')
        if project_id:
            qs = qs.filter(project_id=project_id)
        product_line_id = self.request.query_params.get('product_line')
        if product_line_id:
            qs = qs.filter(project__product_line_id=product_line_id)
        return qs


@extend_schema(tags=["Suite"])
class GlobalVariableViewSet(viewsets.ModelViewSet):
    """全局变量 CRUD"""
    serializer_class = GlobalVariableSerializer
    queryset = GlobalVariable.objects.select_related('environment').order_by('-id')
    permission_classes = [permissions.IsAuthenticated]

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
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get('project')
        if project_id:
            qs = qs.filter(project_id=project_id)
        product_line_id = self.request.query_params.get('product_line')
        if product_line_id:
            qs = qs.filter(project__product_line_id=product_line_id)
        return qs


@extend_schema(tags=["DataSet"])
class DataSetViewSet(viewsets.ModelViewSet):
    """
    参数化数据集 CRUD + 文件上传解析。
    上传 CSV/Excel 后自动解析列名和数据行，存入 columns/rows 字段。
    执行用例/套件时传入 dataset_id，引擎会逐行注入 ${参数名} 变量。
    """
    serializer_class = DataSetSerializer
    queryset = DataSet.objects.select_related('project', 'created_by').order_by('-created_at')
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get('project')
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(created_by=user)

    @action(methods=['POST'], detail=False, url_path='upload')
    def upload(self, request):
        """
        上传 CSV 或 Excel 文件，自动解析为参数集。
        form-data 字段：file（必填）、name（可选，默认文件名）、project（必填，项目 id）
        """
        import csv
        import io
        import openpyxl
        from rest_framework.parsers import MultiPartParser

        f = request.FILES.get('file')
        if not f:
            return Response({'message': '请上传文件'}, status=status.HTTP_400_BAD_REQUEST)

        project_id = request.data.get('project')
        if not project_id:
            return Response({'message': 'project 字段必填'}, status=status.HTTP_400_BAD_REQUEST)

        filename = f.name
        columns, rows = [], []

        try:
            if filename.endswith('.csv'):
                text = f.read().decode('utf-8-sig')
                reader = csv.reader(io.StringIO(text))
                for i, row in enumerate(reader):
                    if not any(row):  # 跳过空行
                        continue
                    if i == 0:
                        columns = [c.strip() for c in row]
                    else:
                        rows.append([str(v).strip() for v in row])

            elif filename.endswith(('.xlsx', '.xls')):
                wb = openpyxl.load_workbook(f, read_only=True, data_only=True)
                ws = wb.active
                for i, row in enumerate(ws.iter_rows(values_only=True)):
                    vals = [str(c).strip() if c is not None else '' for c in row]
                    if not any(vals):  # 跳过空行
                        continue
                    if i == 0:
                        columns = vals
                    else:
                        rows.append(vals)
            else:
                return Response(
                    {'message': '仅支持 .csv / .xlsx / .xls 格式'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {'message': f'文件解析失败：{e}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not columns:
            return Response({'message': '文件内容为空或格式不正确'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user if request.user.is_authenticated else None
        ds = DataSet.objects.create(
            name=request.data.get('name') or filename,
            project_id=project_id,
            columns=columns,
            rows=rows,
            created_by=user,
        )
        return Response(DataSetSerializer(ds).data, status=status.HTTP_201_CREATED)


@extend_schema(tags=["Suite"])
class ExecutionSnapshotViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ExecutionSnapshot.objects.prefetch_related('case_snapshots').order_by('-id')
    serializer_class = ExecutionSnapshotSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        snapshot_id = self.request.query_params.get('id')
        if snapshot_id:
            qs = qs.filter(id=snapshot_id)
        scope_type = self.request.query_params.get('scope_type')
        if scope_type:
            qs = qs.filter(scope_type=scope_type)
        scope_id = self.request.query_params.get('scope_id')
        if scope_id:
            qs = qs.filter(scope_id=scope_id)
        return qs


@extend_schema(tags=["Import"])
class ImportJobViewSet(viewsets.ModelViewSet):
    queryset = ImportJob.objects.all().order_by('-id')
    serializer_class = ImportJobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if not (user.is_staff or user.is_superuser):
            allowed_pl_ids = ProductLineMember.objects.filter(user=user).values_list('product_line_id', flat=True)
            qs = qs.filter(product_line_id__in=allowed_pl_ids)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(methods=['POST'], detail=False, url_path='upload_case_file')
    def upload_case_file(self, request):
        f = request.FILES.get('file')
        product_line_id = request.data.get('product_line')
        if not f:
            return Response({'detail': '请上传文件'}, status=status.HTTP_400_BAD_REQUEST)
        if not product_line_id:
            return Response({'detail': 'product_line 必填'}, status=status.HTTP_400_BAD_REQUEST)
        from django.conf import settings
        import os
        base = os.path.join(settings.BASE_DIR, 'upload_yaml', 'imports')
        os.makedirs(base, exist_ok=True)
        path = os.path.join(base, f"{int(__import__('time').time())}_{f.name}")
        with open(path, 'wb') as wf:
            for chunk in f.chunks():
                wf.write(chunk)
        job = ImportJob.objects.create(
            product_line_id=product_line_id,
            scope_type=request.data.get('scope_type') or '',
            scope_id=request.data.get('scope_id') or None,
            file_path=path,
            created_by=request.user,
        )
        return Response(ImportJobSerializer(job).data, status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=True, url_path='start')
    def start(self, request, pk=None):
        from .tasks import run_case_import_job
        job = self.get_object()
        if job.status == ImportJob.Status.RUNNING:
            return Response({'detail': '任务执行中'}, status=status.HTTP_400_BAD_REQUEST)
        run_case_import_job.delay(job.id)
        return Response({'detail': '已提交异步任务'})
