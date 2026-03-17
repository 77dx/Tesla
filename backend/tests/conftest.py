# [DEPRECATED] 2026-03-12
# 此 conftest.py 及 pytest+YAML 执行链路已废弃。
# 新版执行引擎直接在 Django 进程内运行，不再依赖 pytest。
# 保留仅供参考，请勿在新功能中使用。

import yaml
import allure
import json
import time
from apiframetest.commons import yaml_util
from apiframetest.configs import setting

# ====================== 原有 fixture ====================== #

@pytest.fixture(scope="session", autouse=True)
def clear_extract():
    yaml_util.clean(setting.extract_path)


# ====================== YAML 文件收集器 ====================== #

def pytest_collect_file(parent, file_path):
    if file_path.suffix in [".yaml", ".yml"]:
        return YamlFile.from_parent(parent, path=file_path)


class YamlFile(pytest.File):
    def collect(self):
        """读取 yaml 文件并生成测试项 - 支持 DDT"""
        with open(self.path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if isinstance(data, list):
            for index, case in enumerate(data):
                # 检查是否有参数化配置
                if self._has_parametrize(case):
                    yield from self._create_ddt_tests(case, f"{self.path.name}::case_{index}")
                else:
                    yield YamlTest.from_parent(
                        self,
                        name=f"{self.path.name}::case_{index}",
                        case_data=case
                    )
        else:
            # 检查是否有参数化配置
            if self._has_parametrize(data):
                yield from self._create_ddt_tests(data, f"{self.path.name}::case")
            else:
                yield YamlTest.from_parent(
                    self,
                    name=f"{self.path.name}::case",
                    case_data=data
                )

    def _has_parametrize(self, case_data):
        """检查用例是否有参数化配置"""
        return isinstance(case_data, dict) and "parametrize" in case_data

    def _create_ddt_tests(self, case_data, base_name):
        """创建数据驱动测试用例"""
        parametrize_config = case_data["parametrize"]

        if len(parametrize_config) < 2:
            # 参数化配置不完整，回退到普通用例
            yield YamlTest.from_parent(
                self,
                name=base_name,
                case_data=case_data
            )
            return

        # 第一行是参数名
        param_names = parametrize_config[0]

        # 后续行是参数值
        for param_index, param_values in enumerate(parametrize_config[1:]):
            # 创建新的用例数据
            new_case = copy.deepcopy(case_data)

            # 移除参数化配置（避免重复处理）
            new_case.pop("parametrize", None)

            # 应用参数替换
            self._apply_parameters(new_case, param_names, param_values, param_index)

            # 生成测试用例
            yield YamlTest.from_parent(
                self,
                name=f"{base_name}_ddt_{param_index}",
                case_data=new_case,
                param_index=param_index,
                param_values=param_values
            )

    def _apply_parameters(self, case_data, param_names, param_values, param_index):
        """应用参数到用例数据"""
        # 创建参数字典
        params_dict = dict(zip(param_names, param_values))

        # 替换请求数据中的占位符
        if "request" in case_data and "data" in case_data["request"]:
            case_data["request"]["data"] = self._replace_data_placeholders(case_data["request"]["data"], params_dict)

        # 更新用例标题（如果有）
        if "title" in case_data:
            case_data["title"] = f"{case_data['title']} - 数据组{param_index + 1}"

    @staticmethod
    def _replace_data_placeholders(data, params_dict):
        """递归替换数据中的占位符"""
        if isinstance(data, dict):
            for key, value in data.items():
                data[key] = YamlFile._replace_data_placeholders(value, params_dict)
        elif isinstance(data, list):
            return [YamlFile._replace_data_placeholders(item, params_dict) for item in data]
        elif isinstance(data, str):
            # 替换 $ddt{xxx} 格式的占位符
            if data.startswith('$ddt{') and data.endswith('}'):
                param_name = data[5:-1]  # 提取参数名
                return params_dict.get(param_name, data)
        return data


class YamlTest(pytest.Item):
    """每条 YAML 用例 - 支持 DDT"""

    def __init__(self, name, parent, case_data, param_index=None, param_values=None):
        super().__init__(name, parent)
        self.case_data = case_data
        self.param_index = param_index
        self.param_values = param_values
        self.response_data = None
        self.start_time = None
        self.end_time = None

    def runtest(self):
        """执行 YAML 逻辑"""
        self.start_time = time.time()

        try:
            # 添加参数信息到 Allure
            if self.param_index is not None:
                self._add_param_info_to_allure()

            # 添加 Allure 动态信息
            self._add_allure_info()

            # 记录请求信息到 Allure 报告
            self._attach_request_info()

            # 执行实际的API请求
            self.response_data = self._execute_api_request()

            # 记录响应信息到 Allure 报告
            self._attach_response_info()

            # 验证响应结果
            # self._validate_response()

        except Exception as e:
            self._attach_error_info(str(e))
            raise
        finally:
            self.end_time = time.time()
            self._attach_performance_info()

    def _add_param_info_to_allure(self):
        """添加参数化信息到 Allure 报告"""
        if self.param_values:
            param_info = f"参数组 {self.param_index + 1}:\n"
            for i, value in enumerate(self.param_values):
                param_info += f"  参数{i + 1}: {value}\n"

            allure.dynamic.description(param_info)

    def _add_allure_info(self):
        """添加Allure动态信息"""
        # 基础信息
        if "title" in self.case_data:
            allure.dynamic.title(self.case_data["title"])
        if "feature" in self.case_data:
            allure.dynamic.feature(self.case_data["feature"])
        if "story" in self.case_data:
            allure.dynamic.story(self.case_data["story"])

        # 从allure字段获取更详细的信息（如果存在）
        if "allure" in self.case_data:
            allure_config = self.case_data["allure"]
            if "title" in allure_config:
                allure.dynamic.title(allure_config["title"])
            if "feature" in allure_config:
                allure.dynamic.feature(allure_config["feature"])
            if "story" in allure_config:
                allure.dynamic.story(allure_config["story"])
            if "severity" in allure_config:
                severity_map = {
                    "blocker": allure.severity_level.BLOCKER,
                    "critical": allure.severity_level.CRITICAL,
                    "normal": allure.severity_level.NORMAL,
                    "minor": allure.severity_level.MINOR,
                    "trivial": allure.severity_level.TRIVIAL
                }
                severity = allure_config["severity"].lower()
                allure.dynamic.severity(severity_map.get(severity, allure.severity_level.NORMAL))
            if "description" in allure_config:
                # 如果已经有参数信息，就追加
                current_desc = allure_config["description"]
                if hasattr(self, '_param_description'):
                    current_desc = f"{current_desc}\n\n{self._param_description}"
                allure.dynamic.description(current_desc)

    def _attach_request_info(self):
        """附加请求信息到Allure报告"""
        if "request" in self.case_data:
            with allure.step("请求信息"):
                request_data = self.case_data["request"].copy()

                # 添加参数化信息
                param_info = ""
                if self.param_index is not None:
                    param_info = f"\n**  参数组  **: 第 {self.param_index + 1} 组\n"

                # 美化显示请求信息
                request_info = f"""
**  请求方法  **: {request_data.get('method', 'GET')}
**  请求URL  **: {request_data.get('url', '')}{param_info}
**  请求头   **: {json.dumps(request_data.get('headers', {}), indent=2, ensure_ascii=False)}
**  请求参数  **: {json.dumps(request_data.get('params', {}), indent=2, ensure_ascii=False)}
**  请求体  **: {json.dumps(request_data.get('json', request_data.get('data', {})), indent=2, ensure_ascii=False)}"""

                allure.attach(
                    request_info,
                    name="📤 请求详情",
                    attachment_type=allure.attachment_type.TEXT
                )

                # 同时附加原始JSON格式
                allure.attach(
                    json.dumps(self.case_data["request"], indent=2, ensure_ascii=False),
                    name="请求数据(JSON)",
                    attachment_type=allure.attachment_type.JSON
                )

    def _execute_api_request(self):
        """
        执行API请求。
        - 完全基于 apiframetest 的替换方案：${func(args)} 热加载 + ${varName} 上下文替换
        - 响应后按 extract 规则提取变量，写入 extract.yaml（file 模式）或 Redis（redis 模式）
        - 使用 Session(trust_env=False) 绕过 IDE/系统代理，避免 worker 进程中 ProxyError
        """
        import os
        import re
        import yaml as _yaml
        from string import Template
        from apiframetest.configs import setting

        # ================================================================
        # 工具函数：复用 apiframetest 的上下文读写逻辑，不直接导入带问题依赖的模块
        # ================================================================

        def _get_backend():
            return os.getenv("APIFRAME_CONTEXT_BACKEND", "file").lower()

        def _get_redis_client():
            import redis as _redis
            redis_url = (os.getenv("APIFRAME_REDIS_URL")
                         or os.getenv("CELERY_BROKER_URL")
                         or "redis://127.0.0.1:6379/0")
            return _redis.Redis.from_url(redis_url, decode_responses=True)

        def _get_redis_key():
            prefix = os.getenv("APIFRAME_CONTEXT_PREFIX", "")
            return f"{prefix}:context" if prefix else "apiframe:context"

        def _load_ctx():
            """加载完整上下文字典（用于 ${varName} 替换）"""
            if _get_backend() == "redis":
                r = _get_redis_client()
                return r.hgetall(_get_redis_key()) or {}
            try:
                return _yaml.safe_load(open(setting.extract_path, encoding="utf-8")) or {}
            except Exception:
                return {}

        def _yaml_read(key):
            """读取单个变量（对应 DebugTalk.yaml_read，用于 ${yaml_read(key)} 替换）"""
            key = key.strip()
            if _get_backend() == "redis":
                return _get_redis_client().hget(_get_redis_key(), key)
            try:
                return (_yaml.safe_load(open(setting.extract_path, encoding="utf-8")) or {}).get(key)
            except Exception:
                return None

        def _save_var(var_name, value):
            """持久化提取到的变量（对应 extract_util.extract_key 的写入部分）"""
            if _get_backend() == "redis":
                _get_redis_client().hset(_get_redis_key(), var_name, str(value))
            else:
                from apiframetest.commons import yaml_util
                yaml_util.write(setting.extract_path, {var_name: value}, mode='a+')

        def _hot_replace(data_str):
            """
            替换 ${func(args)} 格式。
            目前内联支持 yaml_read(key)，其余函数保留原占位符。
            与 ExtractUtil.hot_replace 逻辑一致，但不依赖 DebugTalk（避免 rsa/jsonpath 导入问题）。
            """
            regexp = r"\$\{(.*?)\((.*?)\)\}"
            for func_name, func_args in re.findall(regexp, data_str):
                func_name = func_name.strip()
                func_args = func_args.strip()
                new_val = None
                if func_name == 'yaml_read':
                    new_val = _yaml_read(func_args)
                if new_val is None:
                    continue
                if isinstance(new_val, str) and new_val.isdigit():
                    new_val = int(new_val)
                data_str = data_str.replace(
                    '${' + func_name + '(' + func_args + ')}', str(new_val)
                )
            return data_str

        def _resolve(req_dict):
            """
            两步替换，完整复现 apiframetest 的替换链路：
              Step1: hot_replace  → 替换 ${yaml_read(key)} 等函数调用格式
              Step2: Template.safe_substitute → 替换 ${token} 等简单变量格式
            """
            req_str = _yaml.safe_dump(req_dict)
            req_str = _hot_replace(req_str)          # Step1
            ctx = _load_ctx()
            if ctx:
                req_str = Template(req_str).safe_substitute(ctx)  # Step2
            return _yaml.safe_load(req_str)

        def _extract_value(response, attr_name, expr, index):
            """从响应中提取变量值，对应 extract_util.extract_key 的提取部分"""
            from jsonpath_ng import parse as jp_parse
            if attr_name == "json":
                matches = jp_parse(expr).find(response.json())
                if matches:
                    return matches[min(index, len(matches) - 1)].value
            elif attr_name == "status_code":
                return response.status_code
            else:  # 正则
                matches = re.findall(expr, response.text)
                if matches:
                    return matches[index]
            return None

        # ================================================================
        # Step 1：替换请求中的占位符
        # ================================================================
        request_config = _resolve(self.case_data["request"])

        method = request_config.get("method", "GET").upper()
        url = request_config.get("url", "")
        headers = request_config.get("headers", {}) or {}

        request_kwargs = {"headers": headers}
        for param_type in ['params', 'data', 'json', 'files']:
            if param_type in request_config:
                request_kwargs[param_type] = request_config[param_type]

        # ================================================================
        # Step 2：发送请求（trust_env=False 绕过系统/IDE 代理）
        # ================================================================
        import requests as _requests
        with allure.step("发送API请求"):
            session = _requests.Session()
            session.trust_env = False
            response = session.request(method, url, **request_kwargs)

            curl_command = self._generate_curl_command(method, url, headers, request_kwargs)
            allure.attach(
                curl_command,
                name="cURL命令",
                attachment_type=allure.attachment_type.TEXT
            )

        # ================================================================
        # Step 3：提取响应变量并持久化（对应 extract_util.extract_key）
        # ================================================================
        extract_rules = self.case_data.get("extract")
        if extract_rules:
            for var_name, rule in extract_rules.items():
                if not rule:
                    continue
                if isinstance(rule, str):
                    attr_name, expr, index = "json", rule, 0
                elif isinstance(rule, list) and len(rule) >= 2:
                    attr_name = rule[0]
                    expr = rule[1]
                    index = int(rule[2]) if len(rule) >= 3 else 0
                else:
                    continue
                try:
                    value = _extract_value(response, attr_name, expr, index)
                    if value is not None:
                        _save_var(var_name, value)
                        allure.attach(
                            f"{var_name} = {value!r}",
                            name=f"变量提取成功: {var_name}",
                            attachment_type=allure.attachment_type.TEXT
                        )
                    else:
                        allure.attach(
                            f"表达式 {expr!r} 无匹配",
                            name=f"变量提取为空: {var_name}",
                            attachment_type=allure.attachment_type.TEXT
                        )
                except Exception as e:
                    allure.attach(
                        str(e),
                        name=f"变量提取失败: {var_name}",
                        attachment_type=allure.attachment_type.TEXT
                    )

        return response

    def _generate_curl_command(self, method, url, headers, request_kwargs):
        """生成curl命令用于调试"""
        curl_parts = [f"curl -X {method}"]

        # 添加headers
        for key, value in headers.items():
            curl_parts.append(f"-H '{key}: {value}'")

        # 添加请求体数据
        if 'json' in request_kwargs:
            json_data = json.dumps(request_kwargs['json'], ensure_ascii=False)
            curl_parts.append(f"-d '{json_data}'")
        elif 'data' in request_kwargs:
            # 处理表单数据
            data_parts = []
            for key, value in request_kwargs['data'].items():
                data_parts.append(f"{key}={value}")
            curl_parts.append(f"-d '{'&'.join(data_parts)}'")

        curl_parts.append(f"'{url}'")
        return " \\\n  ".join(curl_parts)

    def _attach_response_info(self):
        """附加响应信息到Allure报告"""
        if self.response_data:
            with allure.step("响应信息"):
                response = self.response_data

                # 基础响应信息
                response_info = f"""
**  状态码  **: {response.status_code}
**  响应时间  **: {self._calculate_response_time():.3f}秒
**  响应头  **: {json.dumps(dict(response.headers), indent=2, ensure_ascii=False)}"""

                allure.attach(
                    response_info,
                    name="📥 响应详情",
                    attachment_type=allure.attachment_type.TEXT
                )

                # 响应体内容
                try:
                    # 尝试解析为JSON
                    response_json = response.json()
                    allure.attach(
                        json.dumps(response_json, indent=2, ensure_ascii=False),
                        name="响应体(JSON)",
                        attachment_type=allure.attachment_type.JSON
                    )

                except (ValueError, json.JSONDecodeError):
                    # 如果不是JSON，则作为文本显示
                    allure.attach(
                        response.text,
                        name="响应体(Text)",
                        attachment_type=allure.attachment_type.TEXT
                    )

    def _calculate_response_time(self):
        """计算响应时间"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0

    def _attach_error_info(self, error_message):
        """附加错误信息到报告"""
        with allure.step("❌ 执行失败"):
            # 添加参数信息到错误信息
            if self.param_index is not None:
                error_message = f"参数组 {self.param_index + 1} 执行失败:\n{error_message}"

            allure.attach(
                error_message,
                name="错误信息",
                attachment_type=allure.attachment_type.TEXT
            )

    def _attach_performance_info(self):
        """附加性能信息"""
        response_time = self._calculate_response_time()
        if response_time > 0:
            performance_info = f"总执行时间: {response_time:.3f}秒"

            # 根据响应时间给出建议
            if response_time > 5:
                performance_info += "\n⚠️ 警告: 响应时间较长，建议优化"
            elif response_time > 2:
                performance_info += "\nℹ️ 提示: 响应时间正常"
            else:
                performance_info += "\n✅ 优秀: 响应时间很快"

            allure.attach(
                performance_info,
                name="性能信息",
                attachment_type=allure.attachment_type.TEXT
            )

