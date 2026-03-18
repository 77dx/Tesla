import json
import logging
import os.path
import subprocess
import time
import allure
from pathlib import Path
from django.http import JsonResponse
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from Tesla import settings
from .models import Endpoint, Case
from .serializers import EndpointSerializer, CaseSerializer
from .util import GenerateCase

logger = logging.getLogger(__name__)

from snippet.base_viewset import BaseViewSet


@extend_schema(tags=["Case_API"])
class EndpointViewSet(BaseViewSet):
    queryset = Endpoint.objects.all().order_by('-id')
    serializer_class = EndpointSerializer
    search_fields = ['name', 'url']

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get('project')
        if project_id:
            qs = qs.filter(project_id=project_id)
        method = self.request.query_params.get('method')
        if method:
            qs = qs.filter(method=method)
        return qs


@extend_schema(tags=["Case_API"])
class CaseViewSet(BaseViewSet):
    queryset = Case.objects.all().order_by('-id')
    serializer_class = CaseSerializer
    search_fields = ['name', 'id']

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get('project')
        if project_id:
            qs = qs.filter(project_id=project_id)
        endpoint_id = self.request.query_params.get('endpoint')
        if endpoint_id:
            qs = qs.filter(endpoint_id=endpoint_id)
        return qs

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
    body: { "case_id": 9 }

    用新引擎（CaseRunner）直接执行单条用例，同步返回结果。
    """
    if request.method != 'POST':
        return JsonResponse({'code': 405, 'message': 'Method not allowed'}, status=405)
    try:
        req = json.loads(request.body)
        case_id = req.get('case_id')
        if not case_id:
            return JsonResponse({'code': 400, 'message': 'case_id 必填'}, status=400)

        from case_api.engine import CaseRunner, ContextStore

        ctx = ContextStore(result_id=0, backend='memory')
        runner = CaseRunner(ctx=ctx)
        case_result = runner.run_case(int(case_id))
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
                'extracted':  d.get('extracted') or {},
                'assertions': d.get('assertions') or [],
                'error':      d.get('error') or '',
            }
        })
    except Exception as e:
        logger.exception(e)
        return JsonResponse({'code': 500, 'message': f'执行异常: {e}'}, status=500)

