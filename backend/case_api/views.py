import json
import logging
import os.path
import subprocess
import time
from pathlib import Path
try:
    import allure
except Exception:
    allure = None
from django.http import JsonResponse
from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from Tesla import settings
from .models import Endpoint, Case, CaseNode
from .serializers import EndpointSerializer, CaseSerializer, CaseNodeSerializer
from .util import GenerateCase
from product_line.models import ProductLineMember
from rest_framework.exceptions import PermissionDenied

logger = logging.getLogger(__name__)

from snippet.base_viewset import BaseViewSet


@extend_schema(tags=["Case_API"])
class EndpointViewSet(BaseViewSet):
    queryset = Endpoint.objects.all().order_by('-id')
    serializer_class = EndpointSerializer
    search_fields = ['name', 'url']
    product_line_field = 'product_line_id'

    def get_queryset(self):
        qs = super().get_queryset()
        method = self.request.query_params.get('method')
        if method:
            qs = qs.filter(method=method)
        return qs

    def perform_create(self, serializer):
        pl_id = serializer.validated_data.get('product_line_id')
        if not pl_id and serializer.validated_data.get('project'):
            pl_id = serializer.validated_data['project'].product_line_id
        user = self.request.user
        if pl_id and not (user.is_staff or user.is_superuser):
            if not ProductLineMember.objects.filter(user=user, product_line_id=pl_id).exists():
                raise PermissionDenied('无该产品线权限')
        serializer.save(product_line_id=pl_id, created_by=user if user.is_authenticated else None, updated_by=user if user.is_authenticated else None)

    def perform_update(self, serializer):
        pl_id = serializer.validated_data.get('product_line_id')
        if not pl_id and serializer.validated_data.get('project'):
            pl_id = serializer.validated_data['project'].product_line_id
        user = self.request.user
        if pl_id and not (user.is_staff or user.is_superuser):
            if not ProductLineMember.objects.filter(user=user, product_line_id=pl_id).exists():
                raise PermissionDenied('无该产品线权限')
        serializer.save(product_line_id=pl_id, updated_by=user if user.is_authenticated else None)


@extend_schema(tags=["Case_API"])
class CaseViewSet(BaseViewSet):
    queryset = Case.objects.all().order_by('-id')
    serializer_class = CaseSerializer
    search_fields = ['name', 'id']
    product_line_field = None

    def get_queryset(self):
        qs = super().get_queryset()
        endpoint_id = self.request.query_params.get('endpoint')
        if endpoint_id:
            qs = qs.filter(endpoint_id=endpoint_id)
        product_line_id = self.request.query_params.get('product_line')
        if product_line_id:
            qs = qs.filter(product_line_id=product_line_id)
        return qs

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        from suite.models import SuiteCaseItem
        refs = SuiteCaseItem.objects.filter(case_api=instance).select_related('suite')
        if refs.exists():
            suite_names = '、'.join(
                set(r.suite.name for r in refs if r.suite)
            )
            return Response(
                {'message': f'该用例已被以下套件引用，无法删除：{suite_names}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        user = self.request.user
        obj = serializer.save(project=None, product_line=None, sprint=None, requirement=None, created_by=user if user.is_authenticated else None, updated_by=user if user.is_authenticated else None)
        root = CaseNode.ensure_root()
        parent_id = self.request.data.get('parent_node_id')
        parent = CaseNode.objects.filter(id=parent_id, node_type=CaseNode.NodeType.FOLDER).first() if parent_id else root
        if not hasattr(obj, 'tree_node'):
            node = CaseNode.objects.create(name=obj.name, parent=parent, node_type=CaseNode.NodeType.CASE, case=obj)
            node.path = f"{parent.path}{node.id}/"
            node.save(update_fields=['path'])


@extend_schema(tags=["Case_API"])
class CaseNodeViewSet(viewsets.GenericViewSet):
    queryset = CaseNode.objects.all().order_by('order_no', 'id')
    serializer_class = CaseNodeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def _can_manage_tree(self, user):
        return user.is_authenticated

    def destroy(self, request, *args, **kwargs):
        """
        删除目录/节点：
        - 仅当该节点下没有任何子节点时允许删除
        - 不允许直接通过这里删除用例节点（用例请在用例列表中删除）
        """
        if not self._can_manage_tree(request.user):
            return Response({'message': '无目录管理权限'}, status=status.HTTP_403_FORBIDDEN)
        node = self.get_object()
        if node.node_type == CaseNode.NodeType.CASE:
            return Response({'message': '用例节点请在用例列表中删除'}, status=status.HTTP_400_BAD_REQUEST)
        if node.children.exists():
            return Response({'message': '该节点下仍有子节点，无法删除'}, status=status.HTTP_400_BAD_REQUEST)
        node.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def list(self, request):
        root = CaseNode.ensure_root()
        for c in Case.objects.filter(tree_node__isnull=True):
            node = CaseNode.objects.create(name=c.name, parent=root, node_type=CaseNode.NodeType.CASE, case=c)
            node.path = f"{root.path}{node.id}/"
            node.save(update_fields=['path'])
        root = CaseNode.objects.get(id=root.id)
        data = self.get_serializer(root).data
        pl_id = request.query_params.get('product_line')
        if pl_id:
            def filter_node(node):
                if node.get('node_type') == 'case':
                    case_obj = node.get('item') or {}
                    case_id = case_obj.get('id')
                    if not case_id:
                        return None
                    case = Case.objects.filter(id=case_id).only('product_line_id').first()
                    return node if case and str(case.product_line_id or '') == str(pl_id) else None
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
        parent = CaseNode.objects.filter(id=parent_id).first() if parent_id else CaseNode.ensure_root()
        if not parent:
            return Response({'message': '父节点不存在'}, status=status.HTTP_404_NOT_FOUND)
        if parent.node_type != CaseNode.NodeType.FOLDER:
            return Response({'message': '仅可在文件夹下创建'}, status=status.HTTP_400_BAD_REQUEST)
        node = CaseNode.objects.create(name=name, parent=parent, node_type=CaseNode.NodeType.FOLDER)
        node.path = f"{parent.path}{node.id}/"
        node.save(update_fields=['path'])
        return Response(self.get_serializer(node).data, status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=False)
    def attach_case(self, request):
        if not self._can_manage_tree(request.user):
            return Response({'message': '无目录管理权限'}, status=status.HTTP_403_FORBIDDEN)
        case_id = request.data.get('case_id')
        parent_id = request.data.get('parent_id')
        if not case_id:
            return Response({'message': 'case_id 必填'}, status=status.HTTP_400_BAD_REQUEST)
        case_obj = Case.objects.filter(id=case_id).first()
        if not case_obj:
            return Response({'message': '用例不存在'}, status=status.HTTP_404_NOT_FOUND)
        parent = CaseNode.objects.filter(id=parent_id).first() if parent_id else CaseNode.ensure_root()
        if not parent or parent.node_type != CaseNode.NodeType.FOLDER:
            return Response({'message': '目标文件夹不存在'}, status=status.HTTP_400_BAD_REQUEST)

        node = CaseNode.objects.filter(case=case_obj).first()
        if node:
            old_prefix = f"{node.path}{node.id}/"
            node.parent = parent
            node.name = case_obj.name
            node.path = f"{parent.path}{node.id}/"
            node.save(update_fields=['parent', 'name', 'path'])
            for child in CaseNode.objects.filter(path__startswith=old_prefix).exclude(id=node.id):
                child.path = child.path.replace(old_prefix, node.path, 1)
                child.save(update_fields=['path'])
        else:
            node = CaseNode.objects.create(name=case_obj.name, parent=parent, node_type=CaseNode.NodeType.CASE, case=case_obj)
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
        node = CaseNode.objects.filter(id=node_id).first() if node_id else CaseNode.ensure_root()
        if not node:
            return Response({'message': '节点不存在'}, status=status.HTTP_404_NOT_FOUND)
        node.name = name
        node.save(update_fields=['name'])
        if node.node_type == CaseNode.NodeType.CASE and node.case:
            node.case.name = name
            node.case.save(update_fields=['name'])
        return Response(self.get_serializer(node).data)

    @action(methods=['POST'], detail=False)
    def move(self, request):
        if not self._can_manage_tree(request.user):
            return Response({'message': '无目录管理权限'}, status=status.HTTP_403_FORBIDDEN)
        node_id = request.data.get('node_id')
        target_parent_id = request.data.get('target_parent_id')
        node = CaseNode.objects.filter(id=node_id).first()
        target_parent = CaseNode.objects.filter(id=target_parent_id).first()
        if not node or not target_parent:
            return Response({'message': '节点不存在'}, status=status.HTTP_404_NOT_FOUND)
        if target_parent.node_type != CaseNode.NodeType.FOLDER:
            return Response({'message': '仅可移动到文件夹'}, status=status.HTTP_400_BAD_REQUEST)
        if node.id == target_parent.id or target_parent.path.startswith(node.path):
            return Response({'message': '不能移动到自身或子节点下'}, status=status.HTTP_400_BAD_REQUEST)

        old_path = node.path
        new_path = f"{target_parent.path}{node.id}/"
        with transaction.atomic():
            node.parent = target_parent
            node.path = new_path
            node.save(update_fields=['parent', 'path'])
            descendants = CaseNode.objects.filter(path__startswith=old_path).exclude(id=node.id)
            for child in descendants:
                child.path = child.path.replace(old_path, new_path, 1)
                child.save(update_fields=['path'])
        return Response(self.get_serializer(node).data)


@action(methods=["POST"], detail=False)
def run_pytest(request):
    try:
        req = json.loads(request.body)
        endpoint_id = req.get("endpoint_id")

        # 1. 生成 YAML 测试文件
        yaml_file = GenerateCase(endpoint_id).to_yaml()
        logger.info(f"生成的 YAML 文件为：{yaml_file}")

        if not yaml_file:
            return JsonResponse({
                "status": "error",
                "message": "生成的 YAML 文件不存在"
            }, status=400)
        logger.info(f"开始为 endpoint_id: {endpoint_id} 生成测试用例")

        # 2. 创建本次运行的独立目录
        timestamp = int(time.time())
        run_id = f"{endpoint_id}_{timestamp}"

        base_report_dir = settings.REPORT_DIR / run_id
        base_report_dir.mkdir(parents=True, exist_ok=True)   # 创建本次报告的目录

        allure_results_dir = base_report_dir / "results"
        allure_report_dir = base_report_dir / "report"

        allure_results_dir.mkdir(parents=True, exist_ok=True)
        allure_report_dir.mkdir(parents=True, exist_ok=True)

        # 3. 构造 pytest 命令
        pytest_cmd = [
            "pytest",
            "-vs",
            # str(settings.TEST_ALL_CASES),  # 直接运行生成的 YAML 文件（需适配测试框架）
            yaml_file,
            f"--alluredir={allure_results_dir}",  # 指定报告数据目录
            # "--clean-alluredir"  # 清理历史数据
        ]
        logger.info(f">>>执行pytest命令: {' '.join(pytest_cmd)}")

        # 3. 执行 pytest 命令（带超时）
        result = subprocess.run(
            pytest_cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 设置超时时间（秒）
            cwd=settings.BASE_DIR  # 指定工作目录（确保路径正确）
        )
        logger.info(f">>>执行结果为：{result.stdout}")

        # 4. 生成Allure报告
        allure_cmd = [
            "allure",
            "generate",
            str(allure_results_dir),
            "-o",
            str(allure_report_dir),
            "--clean"
        ]
        logger.info(f">>>生成Allure报告命令：{' '.join(allure_cmd)}")

        allure_result = subprocess.run(
            allure_cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=settings.BASE_DIR
        )

        # 5. 返回测试结果和报告地址
        report_url = f"http://127.0.0.1:8000/reports/{run_id}/report/index.html"
        report_index_path = allure_report_dir / "index.html"
        report_exists = report_index_path.exists()

        logger.info(f"报告地址为：{report_url}")

        return JsonResponse({
            "status": "success",
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "report_url": report_url if report_exists else None,
            "report_generated": report_exists,
            "run_id": run_id,
            "timestamp": timestamp
        })
    except subprocess.TimeoutExpired:
        return JsonResponse({
            "status": "error",
            "message": "测试执行超时"
        }, status=500)
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"内部错误: {str(e)}"
        }, status=500)


def run_case(request):
    """
    POST /case_api/run_case/
    body: { "case_id": 9, "timeout_seconds": 30 }

    用新引擎（CaseRunner）直接执行单条用例，同步返回结果。
    """
    if request.method != 'POST':
        return JsonResponse({'code': 405, 'message': 'Method not allowed'}, status=405)
    try:
        req = json.loads(request.body)
        case_id = req.get('case_id')
        timeout_seconds = int(req.get('timeout_seconds') or 30)
        environment_id = req.get('environment_id')
        if not case_id:
            return JsonResponse({'code': 400, 'message': 'case_id 必填'}, status=400)

        from case_api.engine import CaseRunner, ContextStore
        from suite.models import Environment, GlobalVariable
        from suite.mock_server import MockManager

        env = None
        case_obj = Case.objects.select_related('endpoint').filter(id=case_id).first()
        if not case_obj:
            return JsonResponse({'code': 400, 'message': f'用例不存在: {case_id}'}, status=400)

        if environment_id:
            env = Environment.objects.filter(id=environment_id).first()
            if not env:
                return JsonResponse({'code': 400, 'message': f'环境不存在: {environment_id}'}, status=400)
        else:
            # 未显式指定环境时，自动按 project + service_key 兜底匹配一个可用环境
            service_key = (case_obj.endpoint.service_key or '').strip()
            candidates = Environment.objects.filter(project_id=case_obj.project_id)
            if service_key:
                for cand in candidates:
                    for svc in (cand.urls or []):
                        if svc.get('var') == service_key and svc.get('url'):
                            env = cand
                            logger.info(f'[run_case] 自动匹配环境: case={case_id}, service_key={service_key}, env={cand.id}-{cand.name}')
                            break
                    if env:
                        break
            if not env:
                env = candidates.filter(base_url__gt='').order_by('id').first()

        ctx = ContextStore(result_id=0, backend='memory')
        if env:
            # 环境级全局变量
            global_vars = dict(
                GlobalVariable.objects.filter(environment=env)
                .values_list('key', 'value')
            )
            if global_vars:
                ctx.set_initial(global_vars)
            # 环境变量
            if env.variables:
                ctx.set_initial(env.variables)
            # base_url 与多服务 URL
            if env.base_url:
                ctx.set('__base_url__', env.base_url)
            if env.urls:
                for svc in env.urls:
                    var = svc.get('var') or svc.get('name', '').replace(' ', '_')
                    url = svc.get('url', '')
                    if var and url:
                        ctx.set(var, url)

        runner = CaseRunner(ctx=ctx, environment=env)

        # --- 参数化执行（DDT）---
        dataset_id = req.get('dataset_id')
        if dataset_id:
            from suite.models import DataSet
            try:
                ds = DataSet.objects.get(id=dataset_id)
            except DataSet.DoesNotExist:
                return JsonResponse({'code': 400, 'message': f'参数集不存在: {dataset_id}'}, status=400)

            all_results = []
            for row_idx, row_data in enumerate(ds.iter_rows()):
                # 每行重置上下文，重新注入环境变量 + 行数据
                row_ctx = ContextStore(result_id=0, backend='memory')
                # 复制环境变量
                for k, v in ctx.get_all().items():
                    row_ctx.set(k, v)
                # 注入本行参数（覆盖同名变量）
                row_ctx.set_initial(row_data)
                row_runner = CaseRunner(ctx=row_ctx, environment=env)
                mock_manager = MockManager.from_environment(env)
                mock_manager.start()
                try:
                    r = row_runner.run_case(int(case_id), timeout_seconds=max(1, timeout_seconds))
                finally:
                    mock_manager.stop()
                d = r.to_dict()
                d['row_index'] = row_idx + 1
                d['row_data']  = row_data
                all_results.append(d)

            total   = len(all_results)
            passed  = sum(1 for r in all_results if r.get('success'))
            return JsonResponse({
                'code': 200,
                'message': 'ok',
                'ddt': True,
                'dataset_name': ds.name,
                'total':  total,
                'passed': passed,
                'failed': total - passed,
                'results': all_results,
            })

        # --- 普通单次执行 ---
        mock_manager = MockManager.from_environment(env)
        mock_manager.start()
        try:
            case_result = runner.run_case(int(case_id), timeout_seconds=max(1, timeout_seconds))
        finally:
            mock_manager.stop()
        d = case_result.to_dict()

        return JsonResponse({
            'code': 200,
            'message': 'ok',
            'result': {
                'case_id':    d['case_id'],
                'case_name':  d['case_name'],
                'success':    d['success'],
                'status_code': d['status_code'],
                'duration':   d['duration'],
                'request_info': d.get('request_info'),
                'response_body': d.get('response_body'),
                'extracted':  d.get('extracted') or {},
                'assertions': d.get('assertions') or [],
                'error':      d.get('error') or '',
            }
        })
    except Exception as e:
        logger.exception(e)
        return JsonResponse({'code': 500, 'message': f'执行异常: {e}'}, status=500)

