import json
import logging
import random
import subprocess
import time
from os.path import exists
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap
from django.http import JsonResponse
from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import api_view, action

from Tesla import settings
from .models import Endpoint, Case
from project.models import Project
from .serializers import EndpointSerializer, CaseSerializer

logger = logging.getLogger(__name__)

@extend_schema(tags=["Case_API"])
class EndpointViewSet(viewsets.ModelViewSet):
    queryset = Endpoint.objects.all()
    serializer_class = EndpointSerializer


@extend_schema(tags=["Case_API"])
class CaseViewSet(viewsets.ModelViewSet):
    queryset = Case.objects.all()
    serializer_class = CaseSerializer

def to_case(endpoint_id):
    """将数据库数据转换成yaml并保存"""
    # 查询接口对应的用例
    case_data_list = Case.objects.filter(endpoint_id=endpoint_id)
    logger.info(f"查询接口的用例{case_data_list}")
    # 查询接口对象
    endpoint = Endpoint.objects.get(pk=endpoint_id)
    logger.info(f"接口信息{endpoint}")
    yaml_data = []
    for case in case_data_list:
        temp_data = CommentedMap()
        # feature--项目
        temp_data["feature"] = Project.objects.get(id=case.project.id).name
        logger.info(f"项目名称{temp_data["feature"]}")
        # story--接口
        temp_data["story"] = endpoint.name
        logger.info(f"接口名称{temp_data["story"]}")
        # title--用例name
        temp_data["title"] = case.name
        logger.info(f"用例名称{temp_data["title"]}")
        # request.method/url/headers/.data/json/parmas/files
        request = {}
        request["method"] = endpoint.method
        request["url"] = endpoint.url
        request["headers"] = endpoint.headers

        for key in ['params', 'data', 'json', 'files']:
            value = case.api_args.get(key)
            if value not in (None, '', {}, []):
                request[key] = case.api_args.get(key)

        temp_data["request"] = request

        # extract
        if case.extract:
            temp_data["extract"] = case.extract
        # validate
        temp_data["validate"] = case.validate
        yaml_data.append(temp_data)

    # 写入yaml文件
    # yaml = YAML()
    # # yaml.representer.ignore_aliases = lambda *data: True  # 关键配置：禁用锚点
    # # yaml.indent(sequence=4, offset=2)
    # # yaml.default_flow_style = False
    # file_path = f"{settings.TEST_YAML_PATH}/{endpoint.name}_{time.time()}.yaml"
    # with open(file_path, 'w', encoding="utf-8") as f:
    #     yaml.dump(yaml_data, f)
    # # 判断文件是否存在
    # if exists(file_path):
    #     return True
    # else:
    #     return False

def ddt_to_case(endpoint_id):
    """将数据库数据转换成yaml并保存"""
    # 查询接口的用例
    case_data_list = Case.objects.filter(endpoint_id=endpoint_id)
    logger.info(f"查询接口的用例{case_data_list}")
    # 查询cased对应的endpoint
    endpoint = Endpoint.objects.get(pk=endpoint_id)
    logger.info(f"接口信息{endpoint}")
    # api框架的数据格式
    yaml_data = {"feature": "", "story": "", "title": "","request":
        {"url": "", "method": "", "headers": {}},"parametrize": [], "extract": {},
                 "validate": {}}
    # feature--项目
    yaml_data["feature"] = Project.objects.get(id=endpoint.project_id).name
    logger.info(f"项目名称{yaml_data["feature"]}")
    # story--接口
    yaml_data["story"] = endpoint.name
    logger.info(f"接口名称{yaml_data["story"]}")
    # title--用例name(ddt的用例名称未实现)
    yaml_data["title"] = endpoint.name
    logger.info(f"用例名称{yaml_data["title"]}")
    # request
    yaml_data["request"]["method"] = endpoint.method
    yaml_data["request"]["url"] = endpoint.url
    yaml_data["request"]["headers"] = endpoint.headers
    # 处理request中data部分
    keys_list = []
    values_list = []
    data_type = ""
    for case in case_data_list:
        # extract
        if case.extract:
            yaml_data["extract"] = case.extract
        # validate
        yaml_data["validate"] = case.validate

        for key in ['params', 'data', 'json', 'files']:
            value = case.api_args.get(key)
            if value not in [None, '', {}, []]:
                yaml_data["request"][key] = value
                data_type = key
        keys_list = [key for key in yaml_data["request"][data_type].keys()]
        value_list = []
        for value in yaml_data["request"][data_type].values():
            l = []
            if len(l) < 2:
                l.append(value)
            value_list.extend(l)
        values_list.append(value_list)

    parametrize = []
    parametrize.append(keys_list)
    parametrize.extend(values_list)
    for key in keys_list:
        yaml_data["request"][data_type][key] = '$ddt{' + key + '}'

    yaml_data["parametrize"] = parametrize

    logger.info(f"要写入的yaml数据为：{yaml_data}")

    # 写入yaml文件
    yaml = YAML()
    yaml.representer.ignore_aliases = lambda *data: True  # 关键配置：禁用锚点
    # yaml.indent(sequence=4, offset=2)
    # yaml.default_flow_style = False
    file_path = f"{settings.TEST_YAML_PATH}/{endpoint.name}_{round(time.time())}.yaml"
    with open(file_path, 'w', encoding="utf-8") as f:
        yaml.dump([yaml_data], f)
    if exists(file_path):
        return True
    return False

@api_view(["POST"])
def run_pytest(request):
    try:
        req = json.loads(request.body)
        endpoint_id = req.get("endpoint_id")

        # 1. 生成 YAML 测试文件
        if not ddt_to_case(endpoint_id):
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
            str(settings.TEST_ALL_CASES),  # 直接运行生成的 YAML 文件（需适配测试框架）
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
        logger.info(f">>>执行结果为：{result}")

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
