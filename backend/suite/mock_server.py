"""
@ Title: Mock 服务管理器（方案一：进程内拦截）
@ Author: Cathy

基于 `responses` 库在进程内拦截 HTTP 请求，无需启动额外服务。
套件执行前调用 MockManager.start()，执行后调用 MockManager.stop()。

Mock 规则格式（存储在 Environment.mock_rules 字段）：
[
  {
    "url":     "https://api.example.com/user",  # 拦截 URL，支持正则字符串
    "method":  "GET",                           # HTTP 方法，* 表示所有方法
    "status":  200,                             # 返回状态码
    "body":    {"code": 0, "data": {}},         # 返回体（dict → JSON，str → 原样）
    "headers": {"X-Mock": "true"},              # 额外响应头（可选）
    "delay":   0                                # 延迟毫秒数（可选，模拟慢响应）
  }
]
"""

import json
import logging
import re
import time
from typing import List, Optional

logger = logging.getLogger(__name__)

# HTTP 方法映射
_ALL_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS']


class MockManager:
    """
    进程内 Mock 管理器。

    使用方式：
        manager = MockManager(rules)
        with manager:
            # 此作用域内的 HTTP 请求按规则拦截
            runner.run(...)

    或手动管理：
        manager.start()
        try:
            runner.run(...)
        finally:
            manager.stop()
    """

    def __init__(self, rules: Optional[List[dict]] = None, log_file=None):
        """
        Args:
            rules:    Mock 规则列表（来自 Environment.mock_rules）
            log_file: 日志文件路径（与 SuiteRunner 共用）
        """
        self.rules = rules or []
        self.log_file = log_file
        self._rsps = None       # responses.RequestsMock 实例
        self._active = False

    # ----------------------------------------------------------
    # 日志
    # ----------------------------------------------------------
    def _log(self, msg: str) -> None:
        logger.info(msg)
        if self.log_file:
            ts = time.strftime('%Y-%m-%d %H:%M:%S')
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(f'[{ts}] [Mock] {msg}\n')
            except Exception:
                pass

    # ----------------------------------------------------------
    # 启动
    # ----------------------------------------------------------
    def start(self) -> bool:
        """
        启动 Mock 拦截。返回 True 表示成功启动，False 表示无规则或依赖缺失。
        """
        if not self.rules:
            self._log('无 Mock 规则，跳过 Mock 启动')
            return False

        try:
            import responses as _responses
        except ImportError:
            self._log('WARNING: responses 库未安装，Mock 功能不可用。请执行: pip install responses')
            return False

        self._rsps = _responses.RequestsMock(
            assert_all_requests_are_fired=False,
            passthrough_prefixes=(),   # 未匹配规则的请求正常放行
        )
        # responses 默认会阻断未注册的请求，需要开启 passthrough
        self._rsps.start()
        self._active = True

        registered = 0
        for rule in self.rules:
            try:
                self._register_rule(rule)
                registered += 1
            except Exception as e:
                self._log(f'WARNING: 注册 Mock 规则失败 {rule}: {e}')

        self._log(f'Mock 已启动，共注册 {registered}/{len(self.rules)} 条规则')
        return True

    # ----------------------------------------------------------
    # 注册单条规则
    # ----------------------------------------------------------
    def _register_rule(self, rule: dict) -> None:
        import responses as _responses

        url     = rule.get('url', '')
        method  = (rule.get('method') or 'GET').upper()
        status  = int(rule.get('status', 200))
        body    = rule.get('body', {})
        headers = rule.get('headers') or {}
        delay_ms = int(rule.get('delay', 0))

        if not url:
            raise ValueError('url 字段不能为空')

        # 处理响应体
        if isinstance(body, (dict, list)):
            body_str = json.dumps(body, ensure_ascii=False)
            content_type = 'application/json'
        else:
            body_str = str(body)
            content_type = headers.get('Content-Type', 'text/plain')

        # 合并默认 Content-Type
        resp_headers = {'Content-Type': content_type}
        resp_headers.update(headers)

        # 延迟回调（模拟慢响应）
        if delay_ms > 0:
            original_body = body_str
            original_status = status
            original_headers = resp_headers
            delay_s = delay_ms / 1000.0

            def _callback(request):
                time.sleep(delay_s)
                return (original_status, original_headers, original_body)

            resp_kwargs = dict(callback=_callback)
            register_fn = self._rsps.add_callback
        else:
            resp_kwargs = dict(
                body=body_str,
                status=status,
                headers=resp_headers,
                content_type=content_type,
            )
            register_fn = self._rsps.add

        # 判断是否使用正则匹配
        is_regex = bool(re.search(r'[\^$*+?{}\[\]|()]', url))
        url_pattern = re.compile(url) if is_regex else url

        # 注册方法
        methods_to_register = _ALL_METHODS if method == '*' else [method]
        for m in methods_to_register:
            http_method = getattr(_responses, m, None)
            if http_method is None:
                self._log(f'WARNING: 不支持的 HTTP 方法 {m}，跳过')
                continue

            if register_fn == self._rsps.add_callback:
                self._rsps.add_callback(http_method, url_pattern, **resp_kwargs)
            else:
                self._rsps.add(http_method, url_pattern, **resp_kwargs)

            url_desc = f'regex({url})' if is_regex else url
            self._log(f'  ✓ [{m}] {url_desc} → {status}')

    # ----------------------------------------------------------
    # 停止
    # ----------------------------------------------------------
    def stop(self) -> None:
        if self._active and self._rsps:
            try:
                self._rsps.stop()
                self._rsps.reset()
            except Exception as e:
                self._log(f'WARNING: 停止 Mock 时出错: {e}')
            finally:
                self._active = False
                self._rsps = None
                self._log('Mock 已停止')

    # ----------------------------------------------------------
    # 上下文管理器支持
    # ----------------------------------------------------------
    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()

    # ----------------------------------------------------------
    # 工具方法：从 Environment 对象直接创建
    # ----------------------------------------------------------
    @classmethod
    def from_environment(cls, environment, log_file=None) -> 'MockManager':
        """
        从 suite.models.Environment 实例创建 MockManager。

        Args:
            environment: Environment 模型实例（可为 None）
            log_file:    日志文件路径

        Returns:
            MockManager 实例（rules 为空时 start() 直接返回 False）
        """
        rules = []
        if environment and environment.mock_rules:
            rules = environment.mock_rules if isinstance(environment.mock_rules, list) else []
        return cls(rules=rules, log_file=log_file)
