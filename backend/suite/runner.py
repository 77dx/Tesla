"""
@ Title: 套件执行器
@ Author: Cathy
@ Time: 2026/3/12

纯 Django/Python 实现的套件执行器，不依赖 pytest/YAML/apiframetest。
按套件内用例顺序依次执行，每条用例通过 CaseRunner 执行。
"""

import logging
import time
from pathlib import Path
from typing import Dict, List, Optional

from case_api.engine import CaseRunner, CaseResult, ContextStore
from suite.allure_reporter import AllureReporter

logger = logging.getLogger(__name__)


class SuiteRunResult:
    """套件执行汇总结果"""

    def __init__(self, result_id: int):
        self.result_id   = result_id
        self.success:    bool         = False
        self.is_pass:    bool         = False
        self.case_results: List[Dict] = []
        self.total:      int          = 0
        self.passed:     int          = 0
        self.failed:     int          = 0
        self.skipped:    int          = 0
        self.duration:   float        = 0.0
        self.error:      str          = ''

    def to_dict(self) -> Dict:
        return {
            'result_id':    self.result_id,
            'success':      self.success,
            'is_pass':      self.is_pass,
            'total':        self.total,
            'passed':       self.passed,
            'failed':       self.failed,
            'skipped':      self.skipped,
            'duration':     round(self.duration, 3),
            'error':        self.error,
            'case_results': self.case_results,
        }


class SuiteRunner:
    """
    套件执行器：按顺序依次执行套件内所有启用的用例。

    执行流程：
      1. 初始化 ContextStore（清空旧上下文，写入 initial_context）
      2. 按 order 顺序依次调用 CaseRunner.run_case()
      3. 每条用例结果写入日志和汇总
      4. 更新 RunResult 数据库记录状态

    与旧 tasks.py DAG 调度的区别：
      - 不再生成 YAML 文件
      - 不再调用 pytest 子进程
      - 不再使用 Celery chord/group 并发
      - 改为简单的顺序执行，上下文通过 ContextStore 在进程内传递
    """

    def __init__(self, result_id: int, log_file: Optional[Path] = None):
        self.result_id = result_id
        self.log_file  = log_file
        # 使用 Redis backend（Celery worker 中运行）
        self.ctx = ContextStore(
            result_id=result_id,
            backend='redis',
        )

    def _log(self, msg: str) -> None:
        logger.info(msg)
        if self.log_file:
            ts = time.strftime('%Y-%m-%d %H:%M:%S')
            try:
                self.log_file.parent.mkdir(parents=True, exist_ok=True)
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(f'[{ts}] {msg}\n')
            except Exception as e:
                logger.warning(f'写日志失败: {e}')

    def run(
        self,
        case_api_ids: List[int],
        initial_context: Optional[Dict] = None,
        max_retries: int = 0,
        retry_delay: float = 1.0,
        timeout_seconds: int = 0,
        fail_strategy: str = 'continue',
    ) -> SuiteRunResult:
        """
        执行套件。

        Args:
            case_api_ids:    按执行顺序排列的 CaseAPI id 列表
            initial_context: 初始上下文变量（可选）
            max_retries:     单条用例失败后最多重跑次数（0=不重跑）
            retry_delay:     每次重跑前等待秒数
            timeout_seconds: 单条用例超时秒数（0=不限制）
            fail_strategy:   失败策略：'continue'=继续执行 / 'stop'=立即停止

        Returns:
            SuiteRunResult
        """
        from suite.models import RunResult

        suite_result = SuiteRunResult(self.result_id)
        t0 = time.time()

        # --- 初始化上下文 ---
        self.ctx.clear()
        if initial_context:
            self.ctx.set_initial(initial_context)
            self._log(f'初始上下文: {list(initial_context.keys())}')

        # --- 加载变量（优先级由低到高：全局变量 < 环境变量 < 套件变量 < initial_context < 执行中提取值）---
        suite_name = ''
        _environment = None  # 提前初始化，防止 try 块异常时 MockManager 引用报错
        try:
            from suite.models import RunResult as _RR, GlobalVariable
            _db = _RR.objects.select_related('suite__environment', 'suite__project').get(id=self.result_id)
            _suite = _db.suite
            suite_name = _suite.name if _suite else ''
            _environment = _suite.environment if _suite else None

            # 1. 全局变量（环境级）
            if _suite and _suite.environment:
                global_vars = dict(
                    GlobalVariable.objects.filter(environment=_suite.environment)
                    .values_list('key', 'value')
                )
                if global_vars:
                    self.ctx.set_initial(global_vars)
                    self._log(f'[变量] 全局变量 [{_suite.environment.name}] {len(global_vars)} 个: {global_vars}')

            # 2. 环境变量
            if _suite and _suite.environment:
                env = _suite.environment
                if env.variables:
                    self.ctx.set_initial(env.variables)
                    self._log(f'[变量] 环境变量 [{env.name}] {len(env.variables)} 个: {env.variables}')
                # 单 base_url 注入
                if env.base_url:
                    self.ctx.set('__base_url__', env.base_url)
                    self._log(f'[变量] 环境 base_url={env.base_url}')
                # 多服务 URL 注入：每个服务的 var 字段作为变量名
                if env.urls:
                    for svc in env.urls:
                        var = svc.get('var') or svc.get('name', '').replace(' ', '_')
                        url = svc.get('url', '')
                        if var and url:
                            self.ctx.set(var, url)
                    self._log(f'[变量] 环境多服务 URL {len(env.urls)} 个: {[s.get("var") or s.get("name") for s in env.urls]}')

            # 3. 套件变量
            if _suite and _suite.suite_variables:
                self.ctx.set_initial(_suite.suite_variables)
                self._log(f'[变量] 套件变量 {len(_suite.suite_variables)} 个: {_suite.suite_variables}')

            # 4. 套件 headers（存入上下文特殊 key，CaseRunner 取用）
            if _suite and _suite.suite_headers:
                import json as _json
                self.ctx.set('__suite_headers__', _json.dumps(_suite.suite_headers))
                self._log(f'[变量] 套件请求头 {len(_suite.suite_headers)} 个: {_suite.suite_headers}')
        except Exception as e:
            self._log(f'WARNING: 加载环境/变量失败: {e}')
            suite_name = ''

        # 4. initial_context 优先级最高（已在上方加载）

        self._log('=' * 60)
        self._log(f'套件开始执行 (result_id={self.result_id})')
        self._log(f'用例数量: {len(case_api_ids)} 条')
        self._log(f'用例顺序: {case_api_ids}')
        self._log('=' * 60)

        # --- 启动 Mock 服务 ---
        from suite.mock_server import MockManager
        mock_manager = MockManager.from_environment(_environment, log_file=self.log_file)
        mock_started = mock_manager.start()
        if mock_started:
            self._log(f'[Mock] 已启动，共 {len(mock_manager.rules)} 条规则')

        # 初始化 Allure Reporter
        base_dir = self.log_file.parent.parent if self.log_file else None
        allure_reporter = AllureReporter(base_dir, log_file=self.log_file) if base_dir else None

        # 更新状态为「执行中」
        try:
            db_result = RunResult.objects.get(id=self.result_id)
            db_result.status = RunResult.RunStatus.Running
            db_result.save(update_fields=['status'])
        except Exception as e:
            self._log(f'WARNING: 更新 RunResult 状态失败: {e}')

        # --- 逐条执行用例 ---
        # 获取套件关联的环境对象，传给 CaseRunner 用于 URL 解析（_environment 已在上方赋值）
        runner = CaseRunner(ctx=self.ctx, log_file=self.log_file, environment=_environment)
        suite_result.total = len(case_api_ids)

        stop_on_failure = fail_strategy == 'stop'

        for case_id in case_api_ids:
            try:
                case_result: CaseResult = runner.run_case(
                    case_id,
                    max_retries=max_retries,
                    retry_delay=retry_delay,
                    timeout_seconds=timeout_seconds,
                )
                if case_result.retry_count > 0:
                    self._log(f'用例 #{case_id} 经过 {case_result.retry_count} 次重跑后{"通过" if case_result.success else "仍失败"}')
                suite_result.case_results.append(case_result.to_dict())
                if case_result.success:
                    suite_result.passed += 1
                else:
                    suite_result.failed += 1
                    if stop_on_failure:
                        self._log(f'失败策略=stop：用例 #{case_id} 失败，终止后续 {len(case_api_ids) - suite_result.passed - suite_result.failed} 条用例执行')
                        # 写入 Allure 结果后立即终止
                        if allure_reporter:
                            allure_reporter.add_case_result(case_result.to_dict(), suite_name=suite_name)
                        break
                # 写入 Allure 结果
                if allure_reporter:
                    allure_reporter.add_case_result(case_result.to_dict(), suite_name=suite_name)
            except Exception as e:
                suite_result.failed += 1
                cr_dict = {
                    'case_id':  case_id,
                    'case_name': '',
                    'success':  False,
                    'error':    str(e),
                    'duration': 0,
                    'status_code': None,
                    'assertions': [],
                    'extracted': {},
                }
                suite_result.case_results.append(cr_dict)
                if allure_reporter:
                    allure_reporter.add_case_result(cr_dict, suite_name=suite_name)
                self._log(f'ERROR: 用例 #{case_id} 执行异常: {e}')
                if stop_on_failure:
                    self._log(f'失败策略=stop：异常终止套件执行')
                    break

        suite_result.duration = time.time() - t0
        suite_result.is_pass  = suite_result.failed == 0
        suite_result.success  = True  # 执行流程本身成功（不代表用例全部通过）

        # --- 停止 Mock 服务 ---
        mock_manager.stop()

        self._log('=' * 60)
        self._log(f'套件执行完毕')
        self._log(f'总计: {suite_result.total}  通过: {suite_result.passed}  失败: {suite_result.failed}')
        self._log(f'结果: {"✓ 通过" if suite_result.is_pass else "✗ 失败"}')
        self._log(f'耗时: {suite_result.duration:.2f}s')
        self._log('=' * 60)

        # --- 更新 RunResult ---
        try:
            db_result = RunResult.objects.get(id=self.result_id)
            db_result.is_pass = suite_result.is_pass
            db_result.status  = RunResult.RunStatus.Done
            db_result.save(update_fields=['is_pass', 'status'])
        except Exception as e:
            self._log(f'WARNING: 更新 RunResult 最终状态失败: {e}')

        # --- 生成 Allure HTML 报告 ---
        if allure_reporter:
            try:
                self._log('正在生成 Allure 报告...')
                ok = allure_reporter.generate()
                if ok:
                    self._log(f'Allure 报告已生成: {allure_reporter.report_dir}/index.html')
                else:
                    self._log('WARNING: Allure 报告生成失败，降级为简易报告')
                    self._generate_html_report(suite_result)
            except Exception as e:
                self._log(f'WARNING: 生成 Allure 报告异常: {e}，降级为简易报告')
                self._generate_html_report(suite_result)
        else:
            # 没有 log_file（如单元测试场景），生成简易报告
            try:
                self._generate_html_report(suite_result)
            except Exception as e:
                self._log(f'WARNING: 生成简易报告失败: {e}')

        return suite_result

    def _generate_html_report(self, suite_result: 'SuiteRunResult') -> None:
        """生成简易 HTML 报告，供前端「查看报告」按钮使用"""
        import json as _json
        from pathlib import Path

        if not self.log_file:
            return
        report_dir = Path(self.log_file).parent.parent / 'report'
        report_dir.mkdir(parents=True, exist_ok=True)
        report_file = report_dir / 'index.html'

        passed = suite_result.passed
        failed = suite_result.failed
        total  = suite_result.total
        rate   = round(passed / total * 100, 1) if total else 0
        is_pass = suite_result.is_pass
        status_color = '#27ae60' if is_pass else '#e74c3c'
        status_text  = '通过' if is_pass else '失败'
        now = time.strftime('%Y-%m-%d %H:%M:%S')

        # 读取全局日志
        log_content = ''
        try:
            if self.log_file and Path(self.log_file).exists():
                log_content = Path(self.log_file).read_text(encoding='utf-8')
        except Exception:
            pass

        # 构建用例卡片
        cards = ''
        for idx, cr in enumerate(suite_result.case_results):
            cid   = cr.get('case_id', '')
            cname = cr.get('case_name', f'用例 #{cid}')
            ok    = cr.get('success', False)
            sc    = cr.get('status_code') or '-'
            dur   = cr.get('duration', 0)
            retry = cr.get('retry_count', 0)
            is_broken = bool(cr.get('error') and not cr.get('assertions'))
            status_lc = 'pass' if ok else ('broken' if is_broken else 'fail')
            status_label = '通过' if ok else ('BROKEN' if is_broken else '失败')

            # 断言表格
            assert_rows = ''
            for a in (cr.get('assertions') or []):
                aok = a.get('pass', False)
                ac = 'apass' if aok else 'afail'
                assert_rows += (
                    f'<tr class="assert-row {ac}">'
                    f'<td>{"✓" if aok else "✗"}</td>'
                    f'<td>{a.get("name","")}</td>'
                    f'<td><code>{a.get("expect","")}</code></td>'
                    f'<td><code>{a.get("actual","")}</code></td>'
                    f'<td>{a.get("msg","")}</td></tr>'
                )
            assert_block = ''
            if assert_rows:
                assert_block = (
                    '<div class="section-title">断言明细</div>'
                    '<table class="assert-table">'
                    '<thead><tr><th>结果</th><th>断言描述</th><th>期望值</th><th>实际值</th><th>说明</th></tr></thead>'
                    f'<tbody>{assert_rows}</tbody></table>'
                )

            # 提取变量
            ext_block = ''
            if cr.get('extracted'):
                ext_rows = ''.join(
                    f'<tr><td><code>${{{k}}}</code></td><td><code>{v}</code></td></tr>'
                    for k, v in cr['extracted'].items()
                )
                ext_block = (
                    '<div class="section-title">提取变量</div>'
                    f'<table class="ext-table"><tbody>{ext_rows}</tbody></table>'
                )

            # 请求信息
            req_info = cr.get('request_info') or {}
            req_block = ''
            if req_info:
                req_block = (
                    '<div class="section-title">请求信息</div>'
                    f'<pre class="req-pre">{_json.dumps(req_info, ensure_ascii=False, indent=2)}</pre>'
                )

            # 错误信息
            err_block = ''
            if cr.get('error'):
                err_block = f'<div class="error-msg"><span>⚠ 错误：</span>{cr["error"]}</div>'

            # 用例日志片段
            case_log = ''
            if log_content:
                lines = log_content.splitlines()
                start = None
                for i, line in enumerate(lines):
                    if f'执行用例 #{cid}' in line:
                        start = i; break
                if start is not None:
                    end = len(lines)
                    for i in range(start + 1, len(lines)):
                        if '执行用例 #' in lines[i] and f'执行用例 #{cid}' not in lines[i]:
                            end = i; break
                        if '套件执行完毕' in lines[i]:
                            end = i + 1; break
                    case_log = '\n'.join(lines[start:end])
            log_block = ''
            if case_log:
                log_block = (
                    '<div class="section-title">执行日志</div>'
                    f'<pre class="log-pre">{case_log}</pre>'
                )

            retry_badge = f'<span class="retry-badge">重跑{retry}次</span>' if retry > 0 else ''
            cards += (
                f'<div class="case-card {status_lc}" id="case-{idx}">'
                f'<div class="case-header" onclick="toggle({idx})">'
                f'<span class="dot {status_lc}"></span>'
                f'<span class="case-name">#{cid} {cname}</span>{retry_badge}'
                f'<span class="case-meta">{sc} · {dur}s</span>'
                f'<span class="badge {status_lc}">{status_label}</span>'
                f'<span class="chevron" id="chv-{idx}">▼</span></div>'
                f'<div class="case-body" id="body-{idx}">{err_block}{req_block}{assert_block}{ext_block}{log_block}</div>'
                f'</div>'
            )

        # 全局日志
        full_log_block = ''
        if log_content:
            full_log_block = (
                '<div class="full-log-wrap">'
                '<div class="section-title">完整执行日志</div>'
                f'<pre class="log-pre">{log_content}</pre></div>'
            )

        r = 54
        circ = round(2 * 3.14159 * r, 1)
        dash = round(circ * rate / 100, 1)
        verdict_cls = 'pass' if is_pass else 'fail'

        html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>测试报告 #{self.result_id}</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif;background:#f0f2f5;color:#2c3e50}}
.topbar{{background:#1a1a2e;padding:0 40px;height:52px;display:flex;align-items:center;gap:12px}}
.topbar .brand{{color:#e94560;font-size:16px;font-weight:800}}
.topbar .sub{{color:#666;font-size:13px}}
.hero{{background:linear-gradient(135deg,#1a1a2e,#0f3460);padding:36px 40px;color:white}}
.hero-inner{{max-width:1100px;margin:0 auto;display:flex;align-items:center;gap:48px}}
.hero-text h1{{font-size:28px;font-weight:700;margin-bottom:6px}}
.hero-text .dt{{color:#888;font-size:13px;margin-bottom:16px}}
.verdict{{display:inline-block;padding:6px 20px;border-radius:20px;font-weight:700;font-size:14px}}
.verdict.pass{{background:rgba(39,174,96,.2);color:#2ecc71;border:1px solid #27ae60}}
.verdict.fail{{background:rgba(231,76,60,.2);color:#e74c3c;border:1px solid #e74c3c}}
.stats{{max-width:1100px;margin:0 auto;display:grid;grid-template-columns:repeat(4,1fr);gap:16px;padding:24px 40px}}
.sc{{background:white;border-radius:12px;padding:20px 24px;box-shadow:0 1px 4px rgba(0,0,0,.07);display:flex;align-items:center;gap:16px}}
.sc-icon{{width:46px;height:46px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:20px}}
.sc-icon.t{{background:#e3f2fd}}.sc-icon.p{{background:#e8f5e9}}.sc-icon.f{{background:#ffebee}}.sc-icon.r{{background:#fff3e0}}
.sc-val{{font-size:26px;font-weight:700}}.sc-label{{font-size:12px;color:#888;margin-top:2px}}
.main{{max-width:1100px;margin:0 auto;padding:0 40px 40px}}
.case-card{{background:white;border-radius:10px;margin-bottom:10px;box-shadow:0 1px 3px rgba(0,0,0,.06);border-left:4px solid #ddd;overflow:hidden}}
.case-card.pass{{border-left-color:#27ae60}}.case-card.fail{{border-left-color:#e74c3c}}.case-card.broken{{border-left-color:#f39c12}}
.case-header{{display:flex;align-items:center;gap:10px;padding:13px 18px;cursor:pointer;transition:background .15s}}
.case-header:hover{{background:#f8f9fa}}
.dot{{width:9px;height:9px;border-radius:50%;flex-shrink:0}}
.dot.pass{{background:#27ae60}}.dot.fail{{background:#e74c3c}}.dot.broken{{background:#f39c12}}
.case-name{{font-weight:600;font-size:14px;flex:1;color:#2c3e50}}
.case-meta{{font-size:12px;color:#bbb}}
.badge{{font-size:11px;font-weight:700;padding:2px 9px;border-radius:9px}}
.badge.pass{{background:#e8f5e9;color:#27ae60}}.badge.fail{{background:#ffebee;color:#e74c3c}}.badge.broken{{background:#fff3e0;color:#f39c12}}
.retry-badge{{background:#e8f4fd;color:#3498db;font-size:11px;padding:2px 8px;border-radius:8px;font-weight:600}}
.chevron{{color:#ccc;font-size:11px;transition:transform .2s}}
.case-body{{padding:0 18px;max-height:0;overflow:hidden;transition:max-height .35s ease,padding .2s}}
.case-body.open{{max-height:3000px;padding:14px 18px 18px}}
.section-title{{font-size:11px;font-weight:700;color:#999;text-transform:uppercase;letter-spacing:.08em;margin:14px 0 8px;display:flex;align-items:center;gap:6px}}
.section-title:first-child{{margin-top:0}}
.section-title::before{{content:'';width:3px;height:11px;background:#3498db;border-radius:2px;display:inline-block}}
.assert-table,.ext-table{{width:100%;border-collapse:collapse;font-size:13px}}
.assert-table th{{background:#f5f7fa;padding:7px 11px;text-align:left;font-size:11px;font-weight:700;color:#666}}
.assert-table td,.ext-table td{{padding:7px 11px;border-top:1px solid #f3f3f3}}
.assert-row.apass td:first-child{{color:#27ae60;font-weight:700}}
.assert-row.afail{{background:#fff8f8}}.assert-row.afail td:first-child{{color:#e74c3c;font-weight:700}}
.req-pre{{background:#1e1e2e;color:#cdd6f4;padding:13px 15px;border-radius:8px;font-size:12px;line-height:1.6;overflow-x:auto;font-family:'JetBrains Mono','Fira Code',monospace}}
.log-pre{{background:#0d1117;color:#8b949e;padding:13px 15px;border-radius:8px;font-size:12px;line-height:1.6;overflow-x:auto;font-family:'JetBrains Mono','Fira Code',monospace;white-space:pre-wrap;word-break:break-all}}
.error-msg{{background:#fff5f5;border:1px solid #fed7d7;border-radius:8px;padding:9px 13px;color:#c53030;font-size:13px;margin-bottom:6px}}
.error-msg span{{font-weight:700}}
code{{background:#f0f4f8;padding:1px 5px;border-radius:4px;font-family:monospace;font-size:12px;color:#d63384}}
.full-log-wrap{{margin-top:8px}}
</style></head><body>
<div class="topbar"><span class="brand">● Tesla Test</span><span class="sub">测试执行报告</span></div>
<div class="hero"><div class="hero-inner">
  <svg width="128" height="128" viewBox="0 0 128 128">
    <circle cx="64" cy="64" r="{r}" fill="none" stroke="rgba(255,255,255,.1)" stroke-width="12"/>
    <circle cx="64" cy="64" r="{r}" fill="none" stroke="{status_color}" stroke-width="12"
      stroke-dasharray="{dash} {round(circ-dash,1)}" stroke-dashoffset="{round(circ/4,1)}" stroke-linecap="round"/>
    <text x="64" y="60" text-anchor="middle" fill="white" font-size="22" font-weight="700">{rate}%</text>
    <text x="64" y="76" text-anchor="middle" fill="#888" font-size="11">通过率</text>
  </svg>
  <div class="hero-text">
    <h1>执行报告 #{self.result_id}</h1>
    <div class="dt">{now}</div>
    <span class="verdict {verdict_cls}">{status_text}</span>
  </div>
</div></div>
<div class="stats">
  <div class="sc"><div class="sc-icon t">📋</div><div><div class="sc-val">{total}</div><div class="sc-label">总计</div></div></div>
  <div class="sc"><div class="sc-icon p">✅</div><div><div class="sc-val" style="color:#27ae60">{passed}</div><div class="sc-label">通过</div></div></div>
  <div class="sc"><div class="sc-icon f">❌</div><div><div class="sc-val" style="color:#e74c3c">{failed}</div><div class="sc-label">失败</div></div></div>
  <div class="sc"><div class="sc-icon r">⏱</div><div><div class="sc-val">{round(suite_result.duration,1)}s</div><div class="sc-label">总耗时</div></div></div>
</div>
<div class="main">
  <div style="font-size:15px;font-weight:600;margin-bottom:14px;color:#2c3e50">用例执行明细</div>
  {cards}
  {full_log_block}
</div>
<script>
function toggle(i){{
  var b=document.getElementById('body-'+i);
  var c=document.getElementById('chv-'+i);
  b.classList.toggle('open');
  c.style.transform=b.classList.contains('open')?'rotate(180deg)':'';
}}
// 失败用例默认展开
document.querySelectorAll('.case-card.fail,.case-card.broken').forEach(function(el){{
  var id=el.id.replace('case-','');
  document.getElementById('body-'+id).classList.add('open');
  document.getElementById('chv-'+id).style.transform='rotate(180deg)';
}});
</script>
</body></html>"""
        report_file.write_text(html, encoding='utf-8')
        self._log(f'HTML 报告已生成: {report_file}')
