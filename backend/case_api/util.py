import logging
import re
import time
import yaml
from pathlib import Path
from Tesla import settings
from case_api.models import Case, Endpoint
from project.models import Project

logger = logging.getLogger(__name__)

# ===== 全局变量上下文（同一进程内跨用例共享）=====
# key: 变量名, value: 提取到的值
_var_store: dict = {}


def extract_vars(response_json: dict, extract_rules: dict) -> dict:
    """
    从响应 JSON 中按 jsonpath 提取变量并写入全局上下文。

    Args:
        response_json: 接口响应的 JSON 字典
        extract_rules: 支持两种格式：
            - 简单格式: {"token": "$.data.token"}          → 默认取第 0 个匹配
            - 带索引格式: {"token": ["json", "$.data.token", 0]}  → 取第 index 个匹配

    Returns:
        本次提取到的变量字典
    """
    try:
        from jsonpath_ng import parse as jp_parse
    except ImportError:
        logger.error("jsonpath-ng 未安装，请执行: pip install jsonpath-ng")
        return {}

    extracted = {}
    for var_name, rule in extract_rules.items():
        # 解析规则：支持字符串和 ["json", "$.path", index] 两种格式
        if isinstance(rule, str):
            expression, index = rule, 0
        elif isinstance(rule, list) and len(rule) >= 2:
            # 格式: ["json", "$.path"] 或 ["json", "$.path", index]
            expression = rule[1]
            index = int(rule[2]) if len(rule) >= 3 else 0
        else:
            logger.warning(f"[变量提取] {var_name} 规则格式不支持: {rule!r}，跳过")
            continue

        try:
            matches = jp_parse(expression).find(response_json)
            if matches:
                # 按 index 取值，超出范围则取最后一个
                idx = min(index, len(matches) - 1)
                value = matches[idx].value
                _var_store[var_name] = value
                extracted[var_name] = value
                logger.info(f"[变量提取] {var_name} = {value!r}  (表达式: {expression}, index: {idx})")
            else:
                logger.warning(f"[变量提取] 表达式 {expression!r} 无匹配，跳过")
        except Exception as e:
            logger.error(f"[变量提取] 解析 {expression!r} 失败: {e}")
    return extracted


def resolve_vars(obj):
    """
    递归替换对象中所有 ${变量名} 占位符为上下文中的实际值。

    支持 dict / list / str，其他类型原样返回。

    示例：
        # 登录用例提取 token 后，后续用例的 headers 里写：
        # {"Authorization": "Bearer ${token}"}
        # resolve_vars 会自动替换为真实 token 值
    """
    if isinstance(obj, str):
        def _replace(m):
            name = m.group(1)
            val = _var_store.get(name)
            if val is None:
                logger.warning(f"[变量引用] 变量 ${{{name}}} 未找到，保留原文")
                return m.group(0)
            return str(val)
        return re.sub(r'\$\{(\w+)\}', _replace, obj)
    if isinstance(obj, dict):
        return {k: resolve_vars(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [resolve_vars(i) for i in obj]
    return obj


def clear_vars():
    """清空全局变量上下文（每次套件执行前调用）。"""
    _var_store.clear()
    logger.info("[变量上下文] 已清空")


# [DEPRECATED] 2026-03-12
# GenerateCase 已废弃，新版执行引擎不再生成 YAML 文件。
# 请使用 case_api.engine.CaseRunner 直接执行用例。
# 保留仅供参考，请勿在新功能中使用。

class GenerateCase:
    """
    根据单条 Case（用例）或 Endpoint（接口）生成 pytest-yaml 测试文件。

    推荐用法（用例粒度，精准执行）：
        GenerateCase.from_case(case_id).to_yaml(path)

    兼容用法（接口粒度，执行该接口下所有用例）：
        GenerateCase(endpoint_id).to_yaml(path)
    """

    def __init__(self, endpoint_id, case_ids=None):
        """
        endpoint_id: Endpoint 主键
        case_ids: 指定要包含的 Case id 列表，None 表示该接口下全部用例
        """
        self.endpoint_id = endpoint_id
        self.endpoint = Endpoint.objects.get(pk=endpoint_id)
        logger.info(f"接口信息: {self.endpoint}")

        if case_ids is not None:
            self.case_data_list = Case.objects.filter(
                endpoint_id=endpoint_id, id__in=case_ids
            )
        else:
            self.case_data_list = Case.objects.filter(endpoint_id=endpoint_id)
        logger.info(f"查询到的用例: {self.case_data_list}")

        self.feature = Project.objects.get(id=self.endpoint.project_id).name

        # 处理 cookies → headers
        if self.endpoint.cookies:
            cookies_str = ";".join(f"{k}={v}" for k, v in self.endpoint.cookies.items())
            if self.endpoint.headers:
                self.endpoint.headers["cookie"] = cookies_str
            else:
                self.endpoint.headers = {"cookie": cookies_str}

        self.YAML_TEMPLATE = {
            "feature": self.feature,
            "story": self.endpoint.name,
            "title": self.endpoint.name,
            "request": {
                "url": self.endpoint.url,
                "method": self.endpoint.method,
                "headers": self.endpoint.headers
            },
            "parametrize": [],
            "extract": {},
            "validate": {}
        }

    @classmethod
    def from_case(cls, case_id):
        """
        工厂方法：按单条用例 ID 构造，只生成该用例的测试文件。
        """
        case = Case.objects.select_related('endpoint').get(pk=case_id)
        instance = cls(case.endpoint_id, case_ids=[case_id])
        # 用用例名称作为 story/title，便于 Allure 报告区分
        instance.YAML_TEMPLATE["story"] = case.name
        instance.YAML_TEMPLATE["title"] = case.name
        return instance

    def to_yaml(self, path=None):
        """
        将用例数据序列化为 YAML 文件。
        - 若用例的 extract 字段有内容，会写入 YAML 的 extract 节点，
          测试框架执行后会调用 extract_vars() 提取并存储变量。
        - api_args / headers 中的 ${变量名} 占位符会在运行时由
          resolve_vars() 替换为实际值（运行时解析，YAML 中保留占位符）。

        path:
          - None：写入默认路径 TEST_YAML_PATH
          - 目录路径：在该目录下自动命名
          - 文件路径：直接写入

        Returns:
            str: 生成的文件路径，失败返回 None
        """
        yaml_data = {k: v.copy() if isinstance(v, dict) else v
                     for k, v in self.YAML_TEMPLATE.items()}
        yaml_data["request"] = dict(self.YAML_TEMPLATE["request"])

        keys_list = []
        values_list = []
        data_type = ""

        for case in self.case_data_list:
            # --- 数据提取规则 ---
            # extract 格式: {"变量名": "$.jsonpath表达式"}
            # 例如登录用例: {"token": "$.data.token"}
            if case.extract:
                yaml_data["extract"] = case.extract

            yaml_data["validate"] = case.validate

            if not case.api_args:
                continue

            for key in ['params', 'data', 'json', 'files']:
                value = case.api_args.get(key)
                if value not in [None, '', {}, []]:
                    # ${变量名} 占位符保留在 YAML 中，运行时由框架/resolve_vars 替换
                    yaml_data["request"][key] = value
                    data_type = key

            if data_type and data_type in yaml_data["request"]:
                keys_list = list(yaml_data["request"][data_type].keys())
                value_list = [[v] for v in yaml_data["request"][data_type].values()]
                values_list.append([v[0] for v in value_list])

        logger.info(f"入参 keys: {keys_list}, values: {values_list}")

        if len(values_list) > 1 and data_type:
            parametrize = [keys_list] + values_list
            for key in keys_list:
                yaml_data["request"][data_type][key] = '$ddt{' + key + '}'
            yaml_data["parametrize"] = parametrize
        elif len(values_list) == 1 and data_type:
            yaml_data["request"][data_type] = dict(zip(keys_list, values_list[0]))

        # 确定输出路径
        try:
            if path is None:
                file_path = str(
                    settings.TEST_YAML_PATH /
                    f"test_{self.endpoint.name}_{round(time.time())}.yaml"
                )
            else:
                path_obj = Path(path)
                if path_obj.is_dir():
                    story = yaml_data.get('story', self.endpoint.name)
                    file_path = str(
                        path_obj / f"test_{story}_{round(time.time())}.yaml"
                    )
                else:
                    file_path = str(path_obj)

            with open(file_path, 'w', encoding='utf-8') as f:
                data_to_dump = [yaml_data] if len(values_list) > 1 else yaml_data
                yaml.dump(
                    data_to_dump, f,
                    allow_unicode=True,
                    default_flow_style=False,
                    indent=4,
                    sort_keys=False
                )
            logger.info(f"YAML 文件生成成功: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"写入 YAML 文件失败: {e}")
            return None
