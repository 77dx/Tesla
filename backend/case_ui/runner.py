import json
import time
from pathlib import Path
from typing import Optional

from case_api.engine import ContextStore, VarResolver


class UICaseResult:
    def __init__(self, case_id: int, case_name: str):
        self.case_id = case_id
        self.case_name = case_name
        self.success = False
        self.error = ''
        self.duration = 0.0
        self.assertions = []
        self.extracted = {}
        self.retry_count = 0
        self.screenshots = []
        self.execution_logs = []

    def to_dict(self):
        return {
            'case_id': self.case_id,
            'case_name': self.case_name,
            'success': self.success,
            'error': self.error,
            'duration': round(self.duration, 3),
            'assertions': self.assertions,
            'extracted': self.extracted,
            'retry_count': self.retry_count,
            'screenshots': self.screenshots,
            'execution_logs': self.execution_logs,
            'case_type': 'UI',
        }


class UICaseRunner:
    def __init__(self, ctx: ContextStore, log_file: Optional[Path] = None, environment=None, result_dir: Optional[Path] = None):
        self.ctx = ctx
        self.log_file = log_file
        self.environment = environment
        self.result_dir = result_dir
        self.resolver = VarResolver(ctx)

    def _resolve_locator(self, page, locator_type: str, locator: str):
        locator_type = (locator_type or 'css').lower()
        if not locator:
            return None
        if locator_type == 'xpath':
            return page.locator(f'xpath={locator}')
        if locator_type == 'text':
            return page.get_by_text(locator)
        if locator_type == 'id':
            raw_id = locator.lstrip('#')
            return page.locator(f'#{raw_id}:visible')
        return page.locator(f'{locator}:visible') if locator_type == 'css' else page.locator(locator)

    def _prefer_visible_locator(self, locator_obj):
        if locator_obj is None:
            return None
        try:
            count = locator_obj.count()
        except Exception:
            return locator_obj
        if count <= 1:
            return locator_obj
        for idx in range(count):
            candidate = locator_obj.nth(idx)
            try:
                if candidate.is_visible():
                    return candidate
            except Exception:
                continue
        return locator_obj.first

    def _log(self, message: str, result: Optional[UICaseResult] = None):
        if result is not None:
            result.execution_logs.append(message)
        if not self.log_file:
            return
        ts = time.strftime('%Y-%m-%d %H:%M:%S')
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f'[{ts}] {message}\n')

    def _wait_until_visible(self, locator_obj):
        if locator_obj is None:
            return
        locator_obj.wait_for(state='visible')

    def _run_script(self, script: str, page, case):
        if not script:
            return
        local_ctx = self.ctx.get_all()
        local_vars = {
            'ctx': local_ctx,
            'page': page,
            'case': case,
            'json': json,
        }
        exec(script, {}, local_vars)
        for key, value in (local_vars.get('ctx') or {}).items():
            self.ctx.set(key, value)

    def _save_screenshot(self, page, case_id: int, step_index: int) -> str:
        if not self.result_dir:
            return ''
        shot_dir = self.result_dir / 'screenshots'
        shot_dir.mkdir(parents=True, exist_ok=True)
        path = shot_dir / f'ui_case_{case_id}_step_{step_index}.png'
        try:
            page.wait_for_load_state('networkidle', timeout=3000)
        except Exception:
            pass
        page.screenshot(path=str(path), full_page=False, animations='disabled')
        return str(path)

    def run_case(self, case, max_retries: int = 0, retry_delay: float = 1.0, timeout_seconds: int = 0):
        result = UICaseResult(case.id, case.name)
        started = time.time()
        attempts = max_retries + 1
        last_error = ''

        for attempt in range(attempts):
            try:
                result.retry_count = attempt
                result.assertions = []
                result.extracted = {}
                result.screenshots = []
                result.execution_logs = []

                from playwright.sync_api import sync_playwright

                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=False)
                    context = browser.new_context()
                    page = context.new_page()
                    if timeout_seconds:
                        page.set_default_timeout(timeout_seconds * 1000)

                    self._run_script(case.pre_script, page, case)
                    base_url = self.ctx.get('__base_url__') or (self.environment.base_url if self.environment and self.environment.base_url else '')
                    self._log(f'开始执行用例：{case.name}', result)

                    for idx, step in enumerate(case.steps or [], start=1):
                        step = step or {}
                        if not step.get('enabled', True):
                            self._log(f'步骤 {idx} 已跳过：{step.get("name") or step.get("action") or "未命名步骤"}', result)
                            continue
                        action = step.get('action')
                        locator = self.resolver.resolve(step.get('locator') or '')
                        locator_type = step.get('locator_type') or 'css'
                        value = self.resolver.resolve(step.get('value') or '')
                        target = self.resolver.resolve(step.get('target') or '')
                        timeout = int(step.get('timeout') or 0)
                        if timeout:
                            page.set_default_timeout(timeout)
                        obj = self._prefer_visible_locator(self._resolve_locator(page, locator_type, locator))
                        step_name = step.get('name') or action or f'步骤 {idx}'
                        detail = []
                        if target:
                            detail.append(f'target={target}')
                        if locator:
                            detail.append(f'{locator_type}={locator}')
                        if value:
                            detail.append(f'value={value}')
                        detail_text = f'（{"，".join(detail)}）' if detail else ''
                        self._log(f'步骤 {idx} 开始：{step_name} [{action}]{detail_text}', result)

                        if action == 'goto':
                            url = target or case.entry_url or ''
                            if base_url and url.startswith('/'):
                                url = f"{base_url.rstrip('/')}" + url
                            page.goto(url)
                            self._log(f'步骤 {idx} 页面跳转完成：{page.url}', result)
                        elif action == 'reload':
                            page.reload()
                            self._log(f'步骤 {idx} 页面刷新完成：{page.url}', result)
                        elif action == 'click' and obj:
                            self._wait_until_visible(obj)
                            obj.click()
                            self._log(f'步骤 {idx} 点击完成', result)
                        elif action == 'fill' and obj:
                            self._wait_until_visible(obj)
                            obj.fill(str(value))
                            self._log(f'步骤 {idx} 输入完成', result)
                        elif action == 'press' and obj:
                            self._wait_until_visible(obj)
                            obj.press(str(value))
                            self._log(f'步骤 {idx} 按键完成：{value}', result)
                        elif action == 'select' and obj:
                            self._wait_until_visible(obj)
                            obj.select_option(str(value))
                            self._log(f'步骤 {idx} 选择完成：{value}', result)
                        elif action == 'wait_for_selector' and obj:
                            self._wait_until_visible(obj)
                            self._log(f'步骤 {idx} 等待元素完成：{locator}', result)
                        elif action == 'wait_for_text' and value:
                            page.get_by_text(str(value)).wait_for()
                            self._log(f'步骤 {idx} 等待文本完成：{value}', result)
                        elif action == 'assert_text' and obj:
                            self._wait_until_visible(obj)
                            actual = obj.text_content() or ''
                            passed = str(value) in actual
                            result.assertions.append({'name': step.get('name') or 'assert_text', 'type': 'contains', 'expect': value, 'actual': actual, 'pass': passed, 'msg': '' if passed else f'期望包含 {value!r}'})
                            self._log(f'步骤 {idx} 断言文本：{"通过" if passed else "失败"}', result)
                            if not passed:
                                raise AssertionError(f'断言失败: 期望包含 {value!r}, 实际 {actual!r}')
                        elif action == 'assert_visible' and obj:
                            self._wait_until_visible(obj)
                            passed = obj.is_visible()
                            result.assertions.append({'name': step.get('name') or 'assert_visible', 'type': 'visible', 'expect': True, 'actual': passed, 'pass': passed, 'msg': '' if passed else '元素不可见'})
                            self._log(f'步骤 {idx} 可见断言：{"通过" if passed else "失败"}', result)
                            if not passed:
                                raise AssertionError('断言失败: 元素不可见')
                        elif action == 'assert_url':
                            actual = page.url
                            passed = str(value) in actual
                            result.assertions.append({'name': step.get('name') or 'assert_url', 'type': 'contains', 'expect': value, 'actual': actual, 'pass': passed, 'msg': '' if passed else f'URL 不包含 {value!r}'})
                            self._log(f'步骤 {idx} URL 断言：{"通过" if passed else "失败"}', result)
                            if not passed:
                                raise AssertionError(f'断言失败: URL 不包含 {value!r}')
                        elif action == 'extract_text' and obj:
                            self._wait_until_visible(obj)
                            extracted = obj.text_content() or ''
                            save_as = step.get('save_as')
                            if save_as:
                                self.ctx.set(save_as, extracted)
                                result.extracted[save_as] = extracted
                                self._log(f'步骤 {idx} 提取文本完成：{save_as}={extracted}', result)
                        elif action == 'extract_value' and obj:
                            self._wait_until_visible(obj)
                            extracted = obj.input_value()
                            save_as = step.get('save_as')
                            if save_as:
                                self.ctx.set(save_as, extracted)
                                result.extracted[save_as] = extracted
                                self._log(f'步骤 {idx} 提取输入值完成：{save_as}={extracted}', result)
                        elif action == 'extract_attr' and obj:
                            self._wait_until_visible(obj)
                            attr_name = step.get('attr') or 'value'
                            extracted = obj.get_attribute(attr_name) or ''
                            save_as = step.get('save_as')
                            if save_as:
                                self.ctx.set(save_as, extracted)
                                result.extracted[save_as] = extracted
                                self._log(f'步骤 {idx} 提取属性完成：{save_as}={extracted}', result)
                        elif action == 'set_local_storage':
                            key = step.get('key') or step.get('save_as') or ''
                            page.evaluate("([k,v]) => localStorage.setItem(k, v)", [key, str(value)])
                            self._log(f'步骤 {idx} 写入 localStorage：{key}', result)
                        elif action == 'set_session_storage':
                            key = step.get('key') or step.get('save_as') or ''
                            page.evaluate("([k,v]) => sessionStorage.setItem(k, v)", [key, str(value)])
                            self._log(f'步骤 {idx} 写入 sessionStorage：{key}', result)
                        elif action == 'screenshot':
                            shot = self._save_screenshot(page, case.id, idx)
                            if shot:
                                result.screenshots.append(shot)
                                self._log(f'步骤 {idx} 截图完成：{shot}', result)

                    for rule in case.validate or []:
                        if rule.get('type') == 'url_contains':
                            actual = page.url
                            expect = self.resolver.resolve(rule.get('expected') or '')
                            passed = expect in actual
                            result.assertions.append({'name': rule.get('name') or 'url_contains', 'type': 'contains', 'expect': expect, 'actual': actual, 'pass': passed, 'msg': '' if passed else f'URL 不包含 {expect!r}'})
                            if not passed:
                                raise AssertionError(f'URL 不包含 {expect!r}')

                    self._run_script(case.post_script, page, case)
                    context.close()
                    browser.close()

                result.success = True
                result.error = ''
                break
            except ModuleNotFoundError as exc:
                if exc.name == 'playwright':
                    last_error = '未安装 Playwright Python 依赖。当前项目 Python 3.8 环境请先执行：pip install playwright==1.48.0 && python -m playwright install chromium'
                else:
                    last_error = str(exc)
                self._log(f'[UI] case={case.id} attempt={attempt + 1} failed: {last_error}')
                break
            except Exception as exc:
                last_error = str(exc)
                self._log(f'[UI] case={case.id} attempt={attempt + 1} failed: {exc}')
                if attempt < attempts - 1:
                    time.sleep(retry_delay)

        result.error = '' if result.success else last_error
        result.duration = time.time() - started
        return result
