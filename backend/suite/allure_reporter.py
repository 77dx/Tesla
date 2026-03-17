"""
Allure 报告生成器
在新版执行引擎（CaseRunner）中直接写 Allure 结果文件，
执行完毕后调用 allure generate 生成 HTML 报告。
不依赖 pytest。
"""
import json
import logging
import subprocess
import time
import uuid
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class AllureReporter:
    """
    在 SuiteRunner 执行过程中收集 Allure 结果，执行完毕后生成 HTML 报告。

    使用方式：
        reporter = AllureReporter(result_dir)
        reporter.start_suite('套件名')
        reporter.add_case_result(case_result)
        reporter.finish_suite()
        reporter.generate()
    """

    # Allure 状态映射
    STATUS_PASS    = 'passed'
    STATUS_FAIL    = 'failed'
    STATUS_BROKEN  = 'broken'
    STATUS_SKIPPED = 'skipped'

    def __init__(self, base_dir: Path, log_file: Optional[Path] = None):
        """
        Args:
            base_dir: 执行根目录（RunResult.path 对应的 Path）
            log_file: 全局日志文件路径（用于切割每条用例的日志片段）
        """
        self.base_dir    = Path(base_dir)
        self.log_file    = Path(log_file) if log_file else None
        self.results_dir = self.base_dir / 'allure-results'
        self.report_dir  = self.base_dir / 'report'
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self._suite_start = int(time.time() * 1000)
        self._suite_uuid  = str(uuid.uuid4())

    def _write_result(self, data: dict) -> None:
        """写入单个 Allure 结果 JSON 文件"""
        fname = self.results_dir / f'{uuid.uuid4()}-result.json'
        fname.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

    def _write_container(self, data: dict) -> None:
        """写入 Allure 容器（suite 级别）JSON 文件"""
        fname = self.results_dir / f'{uuid.uuid4()}-container.json'
        fname.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

    def add_case_result(self, cr: dict, suite_name: str = '') -> None:
        """
        将单条 CaseResult.to_dict() 转为 Allure 结果文件。

        Args:
            cr:         CaseResult.to_dict() 的返回值
            suite_name: 套件名（用于 Allure 分组）
        """
        case_uuid  = str(uuid.uuid4())
        start_time = int(time.time() * 1000)
        stop_time  = start_time + int(cr.get('duration', 0) * 1000)
        status     = self.STATUS_PASS if cr.get('success') else self.STATUS_FAIL
        if cr.get('error') and not cr.get('assertions'):
            status = self.STATUS_BROKEN  # 网络/异常类失败用 broken 区分

        # 构建步骤（断言明细）
        steps = []
        for a in (cr.get('assertions') or []):
            step_status = self.STATUS_PASS if a['pass'] else self.STATUS_FAIL
            step_name   = f'{a["name"]}：期望 {a["expect"]!r}，实际 {a["actual"]!r}'
            if a['pass']:
                step_name = f'{a["name"]} ✓'
            steps.append({
                'name':   step_name,
                'status': step_status,
                'start':  start_time,
                'stop':   stop_time,
                'steps':  [],
                'attachments': [],
                'parameters':  [],
            })

        # 构建附件（请求/响应信息）
        attachments = []
        req_info = cr.get('request_info') or {}
        if req_info:
            req_text  = json.dumps(req_info, ensure_ascii=False, indent=2)
            req_fname = self.results_dir / f'{case_uuid}-request.json'
            req_fname.write_text(req_text, encoding='utf-8')
            attachments.append({
                'name':   '请求信息',
                'source': req_fname.name,
                'type':   'application/json',
            })

        extracted = cr.get('extracted') or {}
        if extracted:
            ext_text  = json.dumps(extracted, ensure_ascii=False, indent=2)
            ext_fname = self.results_dir / f'{case_uuid}-extracted.json'
            ext_fname.write_text(ext_text, encoding='utf-8')
            attachments.append({
                'name':   '提取变量',
                'source': ext_fname.name,
                'type':   'application/json',
            })

        # 用例执行日志（从全局日志文件按用例名截取）
        case_log = self._slice_case_log(cr)
        if case_log:
            log_fname = self.results_dir / f'{case_uuid}-case.log'
            log_fname.write_text(case_log, encoding='utf-8')
            attachments.append({
                'name':   '执行日志',
                'source': log_fname.name,
                'type':   'text/plain',
            })

        # 错误信息
        status_details = {}
        if not cr.get('success'):
            msg = cr.get('error') or ''
            if not msg and cr.get('assertions'):
                failed_asserts = [a for a in cr['assertions'] if not a['pass']]
                msg = '；'.join(a['msg'] for a in failed_asserts)
            status_details = {'message': msg, 'trace': msg}

        result = {
            'uuid':        case_uuid,
            'historyId':   str(cr.get('case_id', '')),
            'testCaseId':  str(cr.get('case_id', '')),
            'name':        cr.get('case_name') or f'用例 #{cr.get("case_id")}',
            'fullName':    f'{suite_name} / {cr.get("case_name") or cr.get("case_id")}',
            'status':      status,
            'statusDetails': status_details,
            'start':       start_time,
            'stop':        stop_time,
            'steps':       steps,
            'attachments': attachments,
            'parameters':  [
                {'name': '状态码', 'value': str(cr.get('status_code') or '-')},
                {'name': '耗时',   'value': f'{cr.get("duration", 0):.3f}s'},
            ],
            'labels': [
                {'name': 'suite',   'value': suite_name or '测试套件'},
                {'name': 'feature', 'value': suite_name or '接口测试'},
                {'name': 'story',   'value': cr.get('case_name') or ''},
            ],
            'links': [],
        }
        self._write_result(result)
        logger.info(f'[Allure] 写入用例结果: {cr.get("case_name")} [{status}]')

    def _slice_case_log(self, cr: dict) -> str:
        """
        从全局日志文件中截取当前用例相关的日志片段。
        按「执行用例 #case_id」和下一条「执行用例」之间的内容提取。
        """
        if not self.log_file or not self.log_file.exists():
            return ''
        try:
            lines = self.log_file.read_text(encoding='utf-8').splitlines()
            case_id   = cr.get('case_id')
            case_name = cr.get('case_name', '')
            # 找起始行：包含「执行用例 #case_id」的行
            start_idx = None
            for i, line in enumerate(lines):
                if f'执行用例 #{case_id}' in line or \
                   (case_name and f'执行用例 #{case_id} [{case_name}]' in line):
                    start_idx = i
                    break
            if start_idx is None:
                return ''
            # 找结束行：下一条「执行用例」或套件结束标志
            end_idx = len(lines)
            for i in range(start_idx + 1, len(lines)):
                if '执行用例 #' in lines[i] and '执行用例 #' + str(case_id) not in lines[i]:
                    end_idx = i
                    break
                if '套件执行完毕' in lines[i] or '=' * 20 in lines[i]:
                    end_idx = i + 1
                    break
            return '\n'.join(lines[start_idx:end_idx])
        except Exception as e:
            logger.warning(f'[Allure] 切割日志失败: {e}')
            return ''

    def generate(self) -> bool:
        """
        调用 allure generate 生成 HTML 报告。

        Returns:
            True 表示成功，False 表示失败
        """
        allure_cmd = subprocess.run(
            ['allure', 'generate', str(self.results_dir),
             '--output', str(self.report_dir),
             '--clean',
             '--no-analytics'],
            capture_output=True, text=True, timeout=120
        )
        if allure_cmd.returncode == 0:
            logger.info(f'[Allure] 报告已生成: {self.report_dir}/index.html')
            return True
        else:
            logger.error(f'[Allure] 生成失败: {allure_cmd.stderr}')
            return False
