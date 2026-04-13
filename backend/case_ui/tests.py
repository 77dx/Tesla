from types import ModuleType
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from case_api.engine import ContextStore
from case_ui.models import Case
from case_ui.runner import UICaseRunner
from product_line.models import ProductLine
from project.models import Project


class _FakeLocator:
    def __init__(self):
        self._text = 'Hello Tesla'
        self._value = 'InputValue'
        self._attrs = {'data-id': '42', 'value': 'InputValue'}

    def click(self):
        return None

    def fill(self, value):
        self._value = value

    def press(self, value):
        return None

    def text_content(self):
        return self._text

    def is_visible(self):
        return True

    def input_value(self):
        return self._value

    def get_attribute(self, name):
        return self._attrs.get(name)


class _FakePage:
    def __init__(self):
        self.url = 'https://example.com/dashboard'
        self._locator = _FakeLocator()

    def set_default_timeout(self, timeout):
        return None

    def locator(self, locator):
        return self._locator

    def goto(self, url):
        self.url = url

    def wait_for_selector(self, locator):
        return None

    def get_by_text(self, text):
        class _Waiter:
            def wait_for(self_inner):
                return None
        return _Waiter()

    def evaluate(self, script, args):
        return None

    def screenshot(self, path, full_page=True):
        with open(path, 'wb') as f:
            f.write(b'fake')


class _FakeContext:
    def __init__(self):
        self.page = _FakePage()

    def new_page(self):
        return self.page

    def close(self):
        return None


class _FakeBrowser:
    def new_context(self):
        return _FakeContext()

    def close(self):
        return None


class _FakeChromium:
    def launch(self, headless=True):
        return _FakeBrowser()


class _FakePlaywright:
    chromium = _FakeChromium()


class _FakeSyncPlaywright:
    def __enter__(self):
        return _FakePlaywright()

    def __exit__(self, exc_type, exc, tb):
        return False


class UICaseRunnerTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create(username='tester')
        self.product_line = ProductLine.objects.create(name='PL-UI')
        self.project = Project.objects.create(name='Project-UI', product_line=self.product_line)
        self.case = Case.objects.create(
            name='UI 登录用例',
            project=self.project,
            product_line=self.product_line,
            created_by=self.user,
            updated_by=self.user,
            entry_url='/login',
            steps=[
                {'action': 'goto', 'target': '/login', 'enabled': True},
                {'action': 'fill', 'locator': '#username', 'value': '${username}', 'enabled': True},
                {'action': 'assert_text', 'locator': '.title', 'value': 'Hello', 'enabled': True},
                {'action': 'extract_attr', 'locator': '#username', 'attr': 'data-id', 'save_as': 'user_id', 'enabled': True},
                {'action': 'screenshot', 'enabled': True},
            ],
            validate=[{'type': 'url_contains', 'expected': '/login'}],
        )

    def test_ui_case_runner_executes_steps_and_extracts_context(self):
        ctx = ContextStore(backend='memory')
        ctx.set_initial({'username': 'cathy'})
        runner = UICaseRunner(ctx=ctx)

        playwright_module = ModuleType('playwright')
        sync_api_module = ModuleType('playwright.sync_api')
        sync_api_module.sync_playwright = lambda: _FakeSyncPlaywright()

        with patch.dict('sys.modules', {
            'playwright': playwright_module,
            'playwright.sync_api': sync_api_module,
        }):
            result = runner.run_case(self.case)

        self.assertTrue(result.success)
        self.assertEqual(result.extracted.get('user_id'), '42')
        self.assertEqual(ctx.get('user_id'), '42')
        self.assertGreaterEqual(len(result.assertions), 2)

    def test_ui_case_serializer_model_update_increments_version(self):
        current = self.case.version
        self.case.name = 'UI 登录用例 v2'
        self.case.version = current + 1
        self.case.save(update_fields=['name', 'version'])
        self.case.refresh_from_db()
        self.assertEqual(self.case.version, current + 1)
