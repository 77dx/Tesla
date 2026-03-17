"""
@ Title: 接口用例执行引擎
@ Author: Cathy
@ Time: 2026/3/12

纯 Django/Python 实现的接口执行引擎，不依赖 pytest / YAML / apiframetest。

模块：
  ContextStore  - 上下文变量存储（Redis 或内存）
  VarResolver   - 占位符替换 ${varName} / ${func()}
  Extractor     - 从响应中按规则提取变量
  Assertor      - 断言执行
  CaseRunner    - 单条用例执行器
"""

import logging
import os
import re
import time
from typing import Any, Dict, List, Optional, Tuple

import requests as _requests

logger = logging.getLogger(__name__)


# ===========================================================
# ContextStore
# ===========================================================

class ContextStore:
    """
    上下文变量存储，支持 Redis 和内存两种后端。
    Redis 后端用于 Celery 多进程共享；内存后端用于单进程顺序执行。

    环境变量：
        APIFRAME_CONTEXT_BACKEND  'redis' | 'memory'（默认 memory）
        APIFRAME_REDIS_URL        Redis 连接 URL
        APIFRAME_CONTEXT_PREFIX   Redis key 前缀（如 suite:123）
    """

    def __init__(self, result_id: Optional[int] = None, backend: Optional[str] = None):
        self.result_id = result_id
        self._backend = (backend or os.getenv('APIFRAME_CONTEXT_BACKEND', 'memory')).lower()
        self._mem: Dict[str, str] = {}

    def _r(self):
        import redis
        url = (
            os.getenv('APIFRAME_REDIS_URL')
            or os.getenv('CELERY_BROKER_URL')
            or 'redis://127.0.0.1:6379/0'
        )
        return redis.Redis.from_url(url, decode_responses=True)

    def _key(self) -> str:
        prefix = os.getenv('APIFRAME_CONTEXT_PREFIX', '')
        if not prefix and self.result_id:
            prefix = f'suite:{self.result_id}'
        return f'{prefix}:context' if prefix else 'apiframe:context'

    def get(self, name: str) -> Optional[str]:
        if self._backend == 'redis':
            try:
                return self._r().hget(self._key(), name)
            except Exception as e:
                logger.warning(f'[Ctx] Redis get {name} 失败: {e}')
                return None
        return self._mem.get(name)

    def set(self, name: str, value: Any) -> None:
        sv = str(value)
        if self._backend == 'redis':
            try:
                self._r().hset(self._key(), name, sv)
                logger.info(f'[Ctx] set {name}={sv!r} @ {self._key()}')
            except Exception as e:
                logger.error(f'[Ctx] Redis set {name} 失败: {e}')
        else:
            self._mem[name] = sv
            logger.info(f'[Ctx] set {name}={sv!r}')

    def get_all(self) -> Dict[str, str]:
        if self._backend == 'redis':
            try:
                return self._r().hgetall(self._key()) or {}
            except Exception as e:
                logger.warning(f'[Ctx] Redis hgetall 失败: {e}')
                return {}
        return dict(self._mem)

    def clear(self) -> None:
        if self._backend == 'redis':
            try:
                self._r().delete(self._key())
            except Exception as e:
                logger.warning(f'[Ctx] Redis clear 失败: {e}')
        else:
            self._mem.clear()
        logger.info('[Ctx] 已清空')

    def set_initial(self, ctx: Dict[str, Any]) -> None:
        for k, v in ctx.items():
            self.set(k, v)


# ===========================================================
# VarResolver
# ===========================================================

class VarResolver:
    """
    替换请求数据中的占位符：
      ${varName}     - 从 ContextStore 读取
      ${func(args)}  - 调用内置函数（timestamp / uuid）
    """

    def __init__(self, ctx: ContextStore):
        self.ctx = ctx

    @staticmethod
    def _builtin(name: str, args: str) -> Optional[str]:
        name = name.strip()
        if name == 'timestamp':
            return str(int(time.time()))
        if name == 'uuid':
            import uuid
            return str(uuid.uuid4())
        return None

    def _replace_str(self, text: str) -> str:
        if '${' not in text:
            return text
        # Step1: 函数调用 ${func(args)}
        def _func(m):
            r = self._builtin(m.group(1), m.group(2))
            if r is not None:
                logger.info(f'[Resolver] ${{{m.group(1)}({m.group(2)})}} -> {r!r}')
                return r
            logger.warning(f'[Resolver] 不支持函数 {m.group(0)}')
            return m.group(0)
        text = re.sub(r'\$\{(\w+)\(([^)]*)\)\}', _func, text)
        # Step2: 简单变量 ${varName}
        all_vars = self.ctx.get_all()
        if all_vars:
            def _var(m):
                v = all_vars.get(m.group(1))
                if v is not None:
                    logger.info(f'[Resolver] ${{{m.group(1)}}} -> {v!r}')
                    return v
                logger.warning(f'[Resolver] ${{{m.group(1)}}} 未找到，保留原文')
                return m.group(0)
            text = re.sub(r'\$\{(\w+)\}', _var, text)
        return text

    def resolve(self, obj: Any) -> Any:
        """递归替换 dict/list/str"""
        if isinstance(obj, str):
            return self._replace_str(obj)
        if isinstance(obj, dict):
            return {k: self.resolve(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self.resolve(i) for i in obj]
        return obj


# ===========================================================
# Extractor
# ===========================================================

class Extractor:
    """
    从 HTTP 响应中按规则提取变量，写入 ContextStore。

    规则格式：
        {"token": "$.data.token"}                     # 简单 jsonpath
        {"token": ["json", "$.data.token", 0]}         # [attr, expr, index]
        {"status": ["status_code"]}                   # 取状态码
        {"match": ["text", "regex_expr", 0]}           # 正则
    """

    def __init__(self, ctx: ContextStore):
        self.ctx = ctx

    def _parse_rule(self, rule) -> Tuple[str, str, int]:
        if isinstance(rule, str):
            return 'json', rule, 0
        if isinstance(rule, list):
            attr  = rule[0] if len(rule) >= 1 else 'json'
            expr  = rule[1] if len(rule) >= 2 else ''
            index = int(rule[2]) if len(rule) >= 3 else 0
            return attr, expr, index
        raise ValueError(f'不支持的提取规则: {rule!r}')

    def _extract_one(self, response: _requests.Response, attr: str, expr: str, index: int) -> Any:
        if attr == 'status_code':
            return response.status_code
        if attr == 'json':
            data = response.json()
            try:
                from jsonpath_ng import parse as jp
                matches = jp(expr).find(data)
            except ImportError:
                from jsonpath import jsonpath
                matches = [type('M', (), {'value': v})() for v in (jsonpath(data, expr) or [])]
            if not matches:
                raise ValueError(f'jsonpath {expr!r} 无匹配')
            return matches[min(index, len(matches) - 1)].value
        if attr == 'text':
            matches = re.findall(expr, response.text)
            if not matches:
                raise ValueError(f'正则 {expr!r} 无匹配')
            return matches[index]
        raise ValueError(f'不支持的 attr: {attr!r}')

    def extract(self, response: _requests.Response, rules: Dict) -> Dict[str, Any]:
        """执行所有提取规则，写入上下文，返回本次提取字典"""
        extracted = {}
        for var_name, rule in (rules or {}).items():
            try:
                attr, expr, index = self._parse_rule(rule)
                value = self._extract_one(response, attr, expr, index)
                self.ctx.set(var_name, value)
                extracted[var_name] = value
                logger.info(f'[Extractor] ✓ {var_name}={value!r}')
            except Exception as e:
                logger.error(f'[Extractor] ✗ {var_name}: {e}')
        return extracted


# ===========================================================
# Assertor
# ===========================================================

class Assertor:
    """
    执行断言。支持新格式（列表）和旧格式（dict）。

    【新格式】validate 为列表，每条规则是一个 dict：
        [
          {"name": "状态码",    "type": "eq",       "source": "status_code", "expect": 200},
          {"name": "code正确",  "type": "eq",       "source": "jsonpath",    "expr": "$.code",       "expect": "success"},
          {"name": "token存在", "type": "exists",   "source": "jsonpath",    "expr": "$.data.token"},
          {"name": "含关键词",  "type": "contains",  "source": "text",       "expect": "success"},
          {"name": "不为空",    "type": "not_eq",   "source": "jsonpath",    "expr": "$.msg",        "expect": ""},
        ]

    字段说明：
        name    断言描述（必填）
        type    断言类型：eq / not_eq / contains / not_contains / exists / regex
        source  取值来源：status_code / jsonpath / text
        expr    jsonpath 或正则表达式（source=jsonpath/text 时必填）
        index   jsonpath 多结果时取第几个（默认 0）
        expect  期望值（exists 类型不需要）

    【旧格式兼容】validate 为 dict（apiframetest 格式），自动识别并处理：
        {"equals": {"描述": [期望值, [attr, expr, index]]}}
        {"status_code": 200}
    """

    ASSERT_TYPES = {'eq', 'not_eq', 'contains', 'not_contains', 'exists', 'regex'}

    def __init__(self, ctx: ContextStore):
        self.extractor = Extractor(ctx)

    # ----------------------------------------------------------
    # 从响应中取实际值
    # ----------------------------------------------------------
    def _get_actual(self, response: _requests.Response, rule: dict) -> Any:
        source = rule.get('source', 'jsonpath')
        expr   = rule.get('expr', '')
        index  = int(rule.get('index', 0))
        if source == 'status_code':
            return response.status_code
        if source == 'jsonpath':
            return self.extractor._extract_one(response, 'json', expr, index)
        if source == 'text':
            return self.extractor._extract_one(response, 'text', expr, index)
        raise ValueError(f'不支持的 source: {source!r}')

    # ----------------------------------------------------------
    # 执行单条断言
    # ----------------------------------------------------------
    def _assert_one(self, actual: Any, rule: dict) -> bool:
        atype   = rule.get('type', 'eq')
        expect  = rule.get('expect')
        if atype == 'eq':
            return str(actual) == str(expect)
        if atype == 'not_eq':
            return str(actual) != str(expect)
        if atype == 'contains':
            return str(expect) in str(actual)
        if atype == 'not_contains':
            return str(expect) not in str(actual)
        if atype == 'exists':
            return actual is not None and str(actual).strip() != ''
        if atype == 'regex':
            return bool(re.search(str(expect), str(actual)))
        raise ValueError(f'不支持的断言类型: {atype!r}')

    # ----------------------------------------------------------
    # 主入口：新格式（list）
    # ----------------------------------------------------------
    def _assert_new(self, response: _requests.Response, validate: list) -> List[Dict]:
        results = []
        for rule in validate:
            name  = rule.get('name', '未命名断言')
            atype = rule.get('type', 'eq')
            try:
                actual = self._get_actual(response, rule)
                passed = self._assert_one(actual, rule)
                expect = rule.get('expect')
                msg = '' if passed else (
                    f'期望 {expect!r}，实际 {actual!r}' if atype != 'exists'
                    else f'值为空或不存在：{actual!r}'
                )
            except Exception as e:
                actual, passed, msg = None, False, f'断言异常: {e}'
            results.append({
                'name': name, 'type': atype,
                'expect': rule.get('expect'), 'actual': actual,
                'pass': passed, 'msg': msg,
            })
            level = logger.info if passed else logger.warning
            level(f'[Assertor] {"✓" if passed else "✗"} {name}'
                  + (f': {msg}' if msg else ''))
        return results

    # ----------------------------------------------------------
    # 旧格式兼容（dict）
    # ----------------------------------------------------------
    def _assert_legacy(self, response: _requests.Response, validate: dict) -> List[Dict]:
        results = []
        for assert_type, items in validate.items():
            if assert_type == 'status_code':
                actual = response.status_code
                passed = actual == items
                results.append({'name': 'status_code', 'type': 'eq',
                                 'expect': items, 'actual': actual, 'pass': passed,
                                 'msg': '' if passed else f'期望 {items} 实际 {actual}'})
                continue
            if not isinstance(items, dict):
                continue
            for desc, item in items.items():
                try:
                    expected = item[0]
                    target   = item[1]
                    if isinstance(target, list):
                        attr  = target[0] if len(target) >= 1 else 'json'
                        expr  = target[1] if len(target) >= 2 else ''
                        index = int(target[2]) if len(target) >= 3 else 0
                        actual = self.extractor._extract_one(response, attr, expr, index)
                    elif target == 'status_code':
                        actual = response.status_code
                    else:
                        actual = target
                    if assert_type in ('equals', 'eq'):
                        passed = str(actual) == str(expected)
                    elif assert_type == 'contains':
                        passed = str(expected) in str(actual)
                    elif assert_type in ('not_equals', 'not_eq'):
                        passed = str(actual) != str(expected)
                    else:
                        logger.warning(f'[Assertor-legacy] 未知类型 {assert_type}')
                        continue
                    results.append({'name': desc, 'type': assert_type,
                                     'expect': expected, 'actual': actual,
                                     'pass': passed,
                                     'msg': '' if passed else f'期望 {expected!r} 实际 {actual!r}'})
                    (logger.info if passed else logger.warning)(
                        f'[Assertor-legacy] {"✓" if passed else "✗"} {desc}')
                except Exception as e:
                    results.append({'name': desc, 'type': assert_type,
                                     'expect': None, 'actual': None, 'pass': False,
                                     'msg': f'断言异常: {e}'})
                    logger.error(f'[Assertor-legacy] {desc} 异常: {e}')
        return results

    # ----------------------------------------------------------
    # 统一入口
    # ----------------------------------------------------------
    def assert_response(
        self,
        response: _requests.Response,
        validate: Optional[Any]
    ) -> List[Dict]:
        """执行断言，自动识别新/旧格式，返回结果列表"""
        if not validate:
            return []
        if isinstance(validate, list):
            return self._assert_new(response, validate)
        if isinstance(validate, dict):
            return self._assert_legacy(response, validate)
        logger.warning(f'[Assertor] 不支持的 validate 类型: {type(validate)}')
        return []


# ===========================================================
# CaseResult
# ===========================================================

class CaseResult:
    def __init__(self):
        self.case_id:    Optional[int]  = None
        self.case_name:  str            = ''
        self.success:    bool           = False
        self.status_code: Optional[int] = None
        self.response_body: Any         = None
        self.extracted:  Dict           = {}
        self.assertions: List[Dict]     = []
        self.error:      str            = ''
        self.duration:   float          = 0.0
        self.request_info: Dict         = {}
        self.retry_count: int           = 0   # 实际重跑次数

    def to_dict(self) -> Dict:
        return {
            'case_id':    self.case_id,
            'case_name':  self.case_name,
            'success':    self.success,
            'status_code': self.status_code,
            'extracted':  self.extracted,
            'assertions': self.assertions,
            'error':      self.error,
            'duration':   round(self.duration, 3),
            'retry_count': self.retry_count,
        }


# ===========================================================
# CaseRunner
# ===========================================================

class CaseRunner:
    """
    单条 API 用例执行器。

    执行流程：
      1. 加载 Case + Endpoint
      2. VarResolver 替换请求参数中的占位符
      3. requests.Session 发送请求（trust_env=False 绕过代理）
      4. Extractor 提取变量写入 ContextStore
      5. Assertor 执行断言
      6. 写入日志文件
    """

    def __init__(
        self,
        ctx: ContextStore,
        log_file: Optional['Path'] = None,
        environment=None,
    ):
        self.ctx = ctx
        self.log_file = log_file
        self.environment = environment  # suite.models.Environment 实例，可为 None
        self.resolver  = VarResolver(ctx)
        self.extractor = Extractor(ctx)
        self.assertor  = Assertor(ctx)
        self._session  = _requests.Session()
        self._session.trust_env = False  # 绕过系统/IDE 代理

    def _resolve_url(self, ep) -> str:
        """
        优先级：
        1. endpoint.service_key 非空 → 从环境 urls 中按 var 匹配 base_url，拼接 ep.url（路径部分）
        2. 无匹配或无环境 → 直接使用 ep.url（兼容旧数据）
        """
        if ep.service_key and self.environment:
            env_urls = self.environment.urls or []
            for svc in env_urls:
                if svc.get('var') == ep.service_key:
                    base = svc.get('url', '').rstrip('/')
                    path = ep.url.lstrip('/') if ep.url else ''
                    full = f'{base}/{path}' if path else base
                    logger.info(f'[CaseRunner] 环境 URL 解析: service_key={ep.service_key!r} → {full}')
                    return full
            logger.warning(f'[CaseRunner] 环境中未找到 service_key={ep.service_key!r}，回退使用 ep.url')
        return ep.url

    def _log(self, msg: str) -> None:
        """同时写 logger 和 log_file"""
        logger.info(msg)
        if self.log_file:
            ts = time.strftime('%Y-%m-%d %H:%M:%S')
            try:
                self.log_file.parent.mkdir(parents=True, exist_ok=True)
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(f'[{ts}] {msg}\n')
            except Exception as e:
                logger.warning(f'写日志失败: {e}')

    def run_case(self, case_id: int, max_retries: int = 0, retry_delay: float = 1.0,
                  timeout_seconds: int = 0) -> CaseResult:
        """
        执行单条用例，支持失败重跑和超时控制。

        Args:
            case_id:          Case 主键
            max_retries:      失败后最多重跑次数（0=不重跑）
            retry_delay:      每次重跑前等待秒数
            timeout_seconds:  单次执行超时秒数（0=不限制）
        """
        import time as _time
        result = self._run_case_once(case_id, timeout_seconds=timeout_seconds)
        for attempt in range(1, max_retries + 1):
            if result.success:
                break
            self._log(f'用例 #{case_id} 第 {attempt}/{max_retries} 次重跑 (等待 {retry_delay}s)...')
            _time.sleep(retry_delay)
            result = self._run_case_once(case_id, timeout_seconds=timeout_seconds)
            result.retry_count = attempt
        return result

    def _run_case_once(self, case_id: int, timeout_seconds: int = 0) -> CaseResult:
        """
        执行一次用例。timeout_seconds>0 时通过线程超时机制控制。
        """
        if timeout_seconds > 0:
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(self._run_case_impl, case_id)
                try:
                    return future.result(timeout=timeout_seconds)
                except concurrent.futures.TimeoutError:
                    result = CaseResult()
                    result.case_id = case_id
                    result.error = f'用例执行超时（超过 {timeout_seconds}s）'
                    result.success = False
                    self._log(f'TIMEOUT: 用例 #{case_id} 超过 {timeout_seconds}s，强制终止')
                    return result
        return self._run_case_impl(case_id)

    def _run_case_impl(self, case_id: int) -> CaseResult:
        from case_api.models import Case as CaseModel

        result = CaseResult()
        result.case_id = case_id
        t0 = time.time()

        try:
            case = CaseModel.objects.select_related('endpoint').get(pk=case_id)
            result.case_name = case.name
            ep = case.endpoint

            self._log(f"{'─'*50}")
            self._log(f'执行用例 #{case_id} [{case.name}]')
            self._log(f'接口: {ep.name} [{ep.method}] {ep.url}')

            # --- 构建原始请求 ---
            headers = dict(ep.headers or {})
            # cookies 合并到 headers（支持 ${varName} 占位符，由后续 VarResolver 统一替换）
            if ep.cookies:
                cookies_str = '; '.join(f'{k}={v}' for k, v in ep.cookies.items())
                if 'cookie' not in {k.lower() for k in headers}:
                    headers['cookie'] = cookies_str

            # 用例级参数覆盖接口默认参数
            api_args = dict(case.api_args or {})

            # api_args 中的 headers 合并（用例级 headers 优先级高于接口级）
            if 'headers' in api_args:
                case_headers = api_args.pop('headers') or {}
                # 统一 key 小写处理 cookie/cookies
                for k, v in case_headers.items():
                    # 兼容 'Cookies' 写法，统一转为 'cookie'
                    norm_key = 'cookie' if k.lower() in ('cookies', 'cookie') else k
                    headers[norm_key] = v

            # 环境全局 headers 注入（优先级最低，被接口级和用例级覆盖）
            if self.environment and self.environment.headers:
                env_headers = dict(self.environment.headers)
                env_headers.update(headers)  # 接口级/用例级优先
                headers = env_headers

            # 套件 headers 注入（优先级高于环境 headers，低于接口/用例级 headers）
            suite_headers_raw = self.ctx.get('__suite_headers__')
            if suite_headers_raw:
                try:
                    import json as _json
                    suite_headers = _json.loads(suite_headers_raw)
                    # 套件 headers 作为基础，被接口/用例级覆盖
                    merged = dict(suite_headers)
                    merged.update(headers)
                    headers = merged
                except Exception as e:
                    logger.warning(f'[CaseRunner] 解析套件 headers 失败: {e}')

            resolved_url = self._resolve_url(ep)
            raw_request = {
                'url':     resolved_url,
                'method':  ep.method,
                'headers': headers,
            }
            for field in ('params', 'data', 'json'):
                val = api_args.get(field) or getattr(ep, field, None)
                if val:
                    raw_request[field] = val

            # --- 替换占位符 ---
            resolved = self.resolver.resolve(raw_request)
            result.request_info = resolved
            self._log(f'请求: {resolved["method"]} {resolved["url"]}')
            self._log(f'Headers: {resolved.get("headers")}')
            for f in ('params', 'data', 'json'):
                if f in resolved:
                    self._log(f'{f}: {resolved[f]}')

            # --- 发送请求 ---
            method = resolved.pop('method').upper()
            url    = resolved.pop('url')
            response = self._session.request(method, url, **resolved)
            result.status_code = response.status_code
            self._log(f'响应状态码: {response.status_code}')
            try:
                body = response.json()
                result.response_body = body
                self._log(f'响应体: {str(body)[:500]}')
            except Exception:
                result.response_body = response.text
                self._log(f'响应体(text): {response.text[:500]}')

            # --- 提取变量 ---
            if case.extract:
                extracted = self.extractor.extract(response, case.extract)
                result.extracted = extracted
                if extracted:
                    self._log(f'提取变量: {extracted}')

            # --- 断言 ---
            if case.validate:
                assertions = self.assertor.assert_response(response, case.validate)
                result.assertions = assertions
                failed = [a for a in assertions if not a['pass']]
                if failed:
                    self._log(f'断言失败: {failed}')
                else:
                    self._log(f'断言全部通过 ({len(assertions)} 条)')
                # 只要有断言配置就按断言结果判断成功
                result.success = len(failed) == 0
            else:
                # 无断言配置：HTTP 状态码 < 400 视为成功
                result.success = response.status_code < 400
                self._log('无断言配置，按状态码判断')

        except CaseModel.DoesNotExist:
            result.error = f'用例 #{case_id} 不存在'
            self._log(f'ERROR: {result.error}')
        except Exception as e:
            result.error = str(e)
            self._log(f'ERROR: 用例 #{case_id} 执行异常: {e}')
            logger.exception(e)

        result.duration = time.time() - t0
        status = '✓ 通过' if result.success else '✗ 失败'
        self._log(f'用例 #{case_id} {status}  耗时 {result.duration:.2f}s')
        return result
