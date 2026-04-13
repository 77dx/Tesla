import logging
import time
from datetime import datetime
from pathlib import Path
from secrets import token_hex

from croniter import croniter
from django.db import models
from django.utils import timezone
from project.models import Project
from product_line.models import ProductLine
from case_api.models import Case as CaseAPI, CaseNode
from case_ui.models import Case as CaseUI

logger = logging.getLogger(__name__)


class Service(models.Model):
    """
    服务注册表。统一维护服务标识，环境中引用 service.key 配置实际 URL。
    这样可以保证各环境的 var（service_key）绝对一致，避免人为出错。
    """
    objects: models.QuerySet

    key         = models.CharField('服务标识', max_length=64, unique=True,
                                   help_text='全局唯一标识，如 user-site、order-service')
    name        = models.CharField('服务名称', max_length=64)
    description = models.CharField('备注', max_length=250, blank=True)
    project     = models.ForeignKey(Project, on_delete=models.CASCADE,
                                    related_name='services', verbose_name='所属项目')
    created_at  = models.DateTimeField('创建时间', auto_now_add=True, null=True)

    class Meta:
        verbose_name = '服务'
        verbose_name_plural = '服务'
        ordering = ['project', 'name']

    def __str__(self):
        return f'{self.name} ({self.key})'


class Environment(models.Model):
    """
    运行环境配置。
    套件执行时可选择一个环境，引擎会将环境变量注入 ContextStore，
    支持配置多个服务 URL（微服务场景），以及全局请求头。
    """
    objects: models.QuerySet

    name        = models.CharField('环境名称', max_length=64)
    project     = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='environments')
    base_url    = models.CharField('Base URL（兼容旧字段）', max_length=255, blank=True,
                                   help_text='单服务 base_url，建议迁移到 urls 字段')
    urls        = models.JSONField('服务 URL 列表', blank=True, null=True,
                                   help_text='多服务 URL，格式: [{"name": "用户服务", "url": "https://user.example.com", "var": "user_host"}]')
    headers     = models.JSONField('全局请求头', blank=True, null=True,
                                   help_text='注入到所有请求的请求头，如 {"X-Env": "test"}')
    variables   = models.JSONField('环境变量', blank=True, null=True,
                                   help_text='键值对，如 {"host": "test.example.com"}')
    description = models.CharField('备注', max_length=250, blank=True)
    created_at  = models.DateTimeField('创建时间', auto_now_add=True, null=True)

    # Mock 规则列表，格式：
    # [
    #   {
    #     "url": "https://api.example.com/user",   # 拦截的完整 URL（支持正则）
    #     "method": "GET",                          # HTTP 方法，* 表示所有
    #     "status": 200,                            # 返回状态码
    #     "body": {"code": 0, "data": {}},          # 返回体（dict 或字符串）
    #     "headers": {"Content-Type": "application/json"},  # 返回头（可选）
    #     "delay": 0                                # 延迟毫秒数（可选，模拟慢响应）
    #   }
    # ]
    mock_rules  = models.JSONField(
        'Mock 规则', blank=True, null=True,
        help_text='Mock 拦截规则列表，套件执行时自动启用'
    )

    class Meta:
        verbose_name = '运行环境'
        verbose_name_plural = '运行环境'
        ordering = ['project', 'name']

    def __str__(self):
        return f'{self.name} ({self.project.name})'


class GlobalVariable(models.Model):
    """
    全局变量。作用域为环境级，套件执行时若选择了对应环境则自动注入。
    变量会在套件执行前注入 ContextStore（优先级最低，可被套件变量和环境变量覆盖）。
    """
    objects: models.QuerySet

    environment = models.ForeignKey(
        'Environment', on_delete=models.CASCADE,
        related_name='global_variables',
        verbose_name='所属环境'
    )
    key         = models.CharField('变量名', max_length=64)
    value       = models.CharField('变量值', max_length=1024, blank=True)
    description = models.CharField('备注', max_length=250, blank=True)
    created_at  = models.DateTimeField('创建时间', auto_now_add=True, null=True)

    class Meta:
        verbose_name = '全局变量'
        verbose_name_plural = '全局变量'
        unique_together = [('environment', 'key')]
        ordering = ['environment', 'key']

    def __str__(self):
        return f'{self.key}={self.value} @ {self.environment.name}'


class Suite(models.Model):
    """ 测试套件 """
    objects: models.QuerySet

    class RunType(models.TextChoices):
        ONCE = 'O', '单次执行'
        CRON = 'C', '计划任务'
        WebHook = 'W', 'webhook'

    name = models.CharField("套件名称", max_length=32)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    product_line = models.ForeignKey(
        ProductLine, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='suites', verbose_name='所属产品线'
    )
    description = models.CharField('套件描述', max_length=250, blank=True)

    # 运行环境（可选）
    environment = models.ForeignKey(
        'Environment', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='suites',
        verbose_name='运行环境',
    )
    # 套件级变量（优先级高于全局变量，低于用例提取变量）
    suite_variables = models.JSONField(
        '套件变量', blank=True, null=True,
        help_text='键值对，如 {"api_host": "test.example.com"}，可在用例参数中用 ${api_host} 引用'
    )

    # 套件级请求头（优先级高于环境 headers，低于接口/用例级 headers）
    suite_headers = models.JSONField(
        '套件请求头', blank=True, null=True,
        help_text='注入到本套件所有请求的请求头，如 {"Authorization": "Bearer ${token}"}，优先级高于环境 headers'
    )

    # 执行策略
    timeout_seconds = models.PositiveIntegerField(
        '用例超时时间(秒)', default=0,
        help_text='单条用例最大执行秒数，0 表示不限制'
    )
    fail_strategy = models.CharField(
        '失败策略', max_length=16, default='continue',
        choices=[('continue', '继续执行'), ('stop', '立即停止')],
        help_text='某条用例失败后，套件是继续执行还是立即停止'
    )
    retry_count = models.PositiveSmallIntegerField(
        '重试次数', default=0,
        help_text='用例失败后最多重试次数，0 表示不重试'
    )
    retry_delay = models.FloatField(
        '重试间隔(秒)', default=1.0,
        help_text='每次重试前等待秒数'
    )

    run_type = models.CharField("运行类型", choices=RunType.choices, default=RunType.ONCE, max_length=30)
    cron = models.CharField("cron表达式", max_length=30, blank=True)
    cron_next_run_at = models.DateTimeField("下次执行时间", null=True, blank=True)
    hook_key = models.CharField("webhook密钥", max_length=255, blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True, null=True)
    updated_at = models.DateTimeField("修改时间", auto_now=True, null=True)
    created_by = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.SET_NULL, related_name="suite_created", verbose_name="创建人")
    updated_by = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.SET_NULL, related_name="suite_updated", verbose_name="最后修改人")

    def get_case_api_items(self):
        """返回已启用的 API 用例项，按 role（setup→main→teardown）再按 order 排序"""
        from django.db.models import Case, When, IntegerField
        role_order = Case(
            When(role='setup',    then=0),
            When(role='main',     then=1),
            When(role='teardown', then=2),
            default=1,
            output_field=IntegerField(),
        )
        return self.suite_case_items.filter(
            enabled=True, case_type=SuiteCaseItem.CaseType.API
        ).select_related('case_api').annotate(
            role_weight=role_order
        ).order_by('role_weight', 'order')

    def get_case_ui_items(self):
        """返回已启用的 UI 用例项，按 role（setup→main→teardown）再按 order 排序"""
        from django.db.models import Case, When, IntegerField
        role_order = Case(
            When(role='setup',    then=0),
            When(role='main',     then=1),
            When(role='teardown', then=2),
            default=1,
            output_field=IntegerField(),
        )
        return self.suite_case_items.filter(
            enabled=True, case_type=SuiteCaseItem.CaseType.UI
        ).select_related('case_ui').annotate(
            role_weight=role_order
        ).order_by('role_weight', 'order')

    def case_api_count(self):
        return self.suite_case_items.filter(case_type=SuiteCaseItem.CaseType.API).count()

    def case_ui_count(self):
        return self.suite_case_items.filter(case_type=SuiteCaseItem.CaseType.UI).count()

    def _compute_next_cron_run_at(self, base_time=None):
        if self.run_type != self.RunType.CRON or not self.cron:
            return None
        base_time = base_time or timezone.now()
        return croniter(self.cron, base_time).get_next(datetime)

    @classmethod
    def dispatch_due_cron_suites(cls, now=None):
        now = now or timezone.now()
        triggered = 0
        due_suites = cls.objects.filter(
            run_type=cls.RunType.CRON,
            cron__gt='',
            cron_next_run_at__isnull=False,
            cron_next_run_at__lte=now,
        ).order_by('cron_next_run_at', 'id')
        for suite in due_suites:
            suite.run(trigger_source='cron')
            next_run_at = suite._compute_next_cron_run_at(base_time=now)
            cls.objects.filter(pk=suite.pk).update(cron_next_run_at=next_run_at)
            triggered += 1
        return triggered

    def save(self, *args, **kwargs):
        if self.run_type == self.RunType.CRON and self.cron:
            self.cron_next_run_at = self._compute_next_cron_run_at()
        else:
            self.cron_next_run_at = None

        if self.run_type == self.RunType.WebHook and not self.hook_key:
            self.hook_key = token_hex(16)
        return super().save(*args, **kwargs)


    def run(self, case_ids=None, ui_case_ids=None, initial_context=None, dataset_id=None,
            scope_type='project', scope_id=None, trigger_source='manual', product_line=None):
        """
        执行测试套件。

        执行粒度：SuiteCaseItem（用例粒度），而非接口粒度。

        参数:
            case_ids: 指定要执行的 CaseAPI id 列表（None 表示取套件内全部已启用 API 用例）
            ui_case_ids: 指定要执行的 CaseUI id 列表（None 表示取套件内全部已启用 UI 用例）
            initial_context: 初始上下文字典
            product_line: 指定执行结果归属的产品线（可选，默认使用套件或项目的产品线）

        Returns:
            RunResult 对象
        """
        from Tesla import settings

        if scope_id is None:
            scope_id = self.project_id if self.project_id else 0

        # 确定执行结果归属的产品线
        result_product_line = product_line or self.product_line or (self.project.product_line if self.project else None)

        # 1. 创建执行记录
        result: RunResult = RunResult.objects.create(
            suite=self,
            project=self.project,
            scope_type=scope_type,
            scope_id=scope_id,
            product_line=result_product_line,
            trigger_source=trigger_source,
            path="todo"
        )

        # 2. 创建独立执行目录
        base_dir = getattr(settings, 'SUITE_EXECUTION_BASE_DIR', Path('upload_yaml'))
        dir_name = f"result_{result.id}_{int(time.time())}"
        path = Path(base_dir) / dir_name
        path.mkdir(parents=True, exist_ok=True)

        result.path = str(path)
        result.status = RunResult.RunStatus.Ready
        result.save()

        # 3. 构建本次要执行的 SuiteCaseItem 顺序列表（真正支持 API/UI 混编）
        ordered_items = list(
            self.suite_case_items.filter(enabled=True)
            .select_related('case_api__endpoint', 'case_ui')
            .order_by('order', 'id')
        )
        if case_ids is not None:
            if isinstance(case_ids, str):
                case_ids = [int(x.strip()) for x in case_ids.split(',') if x.strip()]
            elif isinstance(case_ids, int):
                case_ids = [case_ids]
            case_id_set = {int(x) for x in case_ids}
            ordered_items = [item for item in ordered_items if not item.case_api_id or item.case_api_id in case_id_set]
        if ui_case_ids is not None:
            if isinstance(ui_case_ids, str):
                ui_case_ids = [int(x.strip()) for x in ui_case_ids.split(',') if x.strip()]
            elif isinstance(ui_case_ids, int):
                ui_case_ids = [ui_case_ids]
            ui_id_set = {int(x) for x in ui_case_ids}
            ordered_items = [item for item in ordered_items if not item.case_ui_id or item.case_ui_id in ui_id_set]

        suite_item_ids = [item.id for item in ordered_items]
        api_case_ids = [item.case_api_id for item in ordered_items if item.case_type == SuiteCaseItem.CaseType.API and item.case_api_id]
        ui_ids = [item.case_ui_id for item in ordered_items if item.case_type == SuiteCaseItem.CaseType.UI and item.case_ui_id]

        # 4. 生成 UI 测试用例文件（兼容旧导出能力）
        for case_ui in CaseUI.objects.filter(id__in=ui_ids):
            case_ui.to_xlsx(path)

        # 5. 生成执行快照（用于结果可追溯）
        from case_api.models import Case as CaseModel
        snapshot = ExecutionSnapshot.objects.create(
            scope_type=scope_type,
            scope_id=scope_id,
            product_line=result_product_line,
            suite=self,
            suite_name=self.name,
        )
        result.snapshot_id = snapshot.id
        result.save(update_fields=['snapshot_id'])

        for c in CaseModel.objects.filter(id__in=api_case_ids).select_related('endpoint'):
            ExecutionCaseSnapshot.objects.create(
                snapshot=snapshot,
                case_id=c.id,
                case_name=c.name,
                case_version=c.version,
                payload_json={
                    'id': c.id,
                    'name': c.name,
                    'case_type': 'API',
                    'version': c.version,
                    'project_id': c.project_id,
                    'product_line_id': c.product_line_id,
                    'endpoint': {
                        'id': c.endpoint_id,
                        'name': c.endpoint.name if c.endpoint else '',
                        'method': c.endpoint.method if c.endpoint else '',
                        'url': c.endpoint.url if c.endpoint else '',
                        'service_key': c.endpoint.service_key if c.endpoint else '',
                    },
                    'api_args': c.api_args,
                    'extract': c.extract,
                    'validate': c.validate,
                    'pre_script': c.pre_script,
                    'post_script': c.post_script,
                }
            )

        for c in CaseUI.objects.filter(id__in=ui_ids):
            ExecutionCaseSnapshot.objects.create(
                snapshot=snapshot,
                case_id=c.id,
                case_name=c.name,
                case_version=c.version,
                payload_json={
                    'id': c.id,
                    'name': c.name,
                    'case_type': 'UI',
                    'version': c.version,
                    'project_id': c.project_id,
                    'product_line_id': c.product_line_id,
                    'platform': c.platform,
                    'entry_url': c.entry_url,
                    'steps': c.steps,
                    'extract': c.extract,
                    'validate': c.validate,
                    'pre_script': c.pre_script,
                    'post_script': c.post_script,
                }
            )

        # 6. 记录套件执行日志（手动独立、定时按策略聚合）
        SuiteExecutionLog.record_run(self, result, trigger_source=trigger_source)

        # 7. 提交 Celery 任务（新版 v2.0：直接调用 SuiteRunner，不再生成 YAML/调用 pytest）
        if suite_item_ids:
            from suite.tasks import run_suite_task
            run_suite_task.delay(
                result.id, suite_item_ids, initial_context or {},
                max_retries=self.retry_count,
                retry_delay=self.retry_delay,
                timeout_seconds=self.timeout_seconds,
                fail_strategy=self.fail_strategy,
                dataset_id=dataset_id,
            )
        else:
            result.status = RunResult.RunStatus.Error
            result.save()

        # [DEPRECATED] 旧版 v1.x 调用方式，已废弃
        # if test_cases_generated:
        #     import shutil
        #     for fname in ['conftest.py', 'pytest.ini']:
        #         src = Path(settings.BASE_DIR) / 'tests' / fname
        #         dst = path / fname
        #         try:
        #             if src.exists():
        #                 shutil.copy2(src, dst)
        #         except Exception as e:
        #             logger.error(f"复制 {fname} 失败: {e}")
        # if test_cases_generated:
        #     from suite.tasks import start_suite_dag
        #     start_suite_dag.delay(result.id, api_case_ids, initial_context or {})

        return result

    def __str__(self):
        return f"Suite({self.id}): {self.name}"


class SuiteNode(models.Model):
    class NodeType(models.TextChoices):
        FOLDER = 'folder', '文件夹'
        SUITE = 'suite', '套件'

    name = models.CharField('名称', max_length=64)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    path = models.CharField('物化路径', max_length=255, default='/', db_index=True)
    node_type = models.CharField('节点类型', max_length=16, choices=NodeType.choices, default=NodeType.FOLDER)
    suite = models.OneToOneField('Suite', null=True, blank=True, on_delete=models.CASCADE, related_name='tree_node')
    order_no = models.PositiveIntegerField('排序', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        ordering = ['order_no', 'id']

    @classmethod
    def ensure_root(cls):
        root = cls.objects.filter(parent__isnull=True, node_type=cls.NodeType.FOLDER).order_by('id').first()
        if root:
            if root.path != '/':
                root.path = '/'
                root.save(update_fields=['path'])
            return root
        root = cls.objects.create(name='根目录', parent=None, path='/', node_type=cls.NodeType.FOLDER)
        return root


class SuiteCaseItem(models.Model):
    """
    测试套件用例项（中间表）

    替代原来的 ManyToMany 直连，支持：
    - 执行顺序（order）
    - 启用/禁用（enabled）
    - 参数覆盖（env_override）：可在运行时覆盖用例的请求参数或环境变量
    - 用例类型（API / UI）
    """
    objects: models.QuerySet

    class CaseType(models.TextChoices):
        API = 'API', 'API用例'
        UI = 'UI', 'UI用例'

    suite = models.ForeignKey(
        Suite, on_delete=models.CASCADE,
        related_name='suite_case_items',
        verbose_name='所属套件'
    )
    case_type = models.CharField(
        '用例类型', max_length=8,
        choices=CaseType.choices, default=CaseType.API
    )
    # API 用例（case_type=API 时有值）
    case_api = models.ForeignKey(
        CaseAPI, null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='suite_items',
        verbose_name='API用例'
    )
    # UI 用例（case_type=UI 时有值）
    case_ui = models.ForeignKey(
        CaseUI, null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='suite_items',
        verbose_name='UI用例'
    )
    class Role(models.TextChoices):
        SETUP    = 'setup',    '前置操作'
        MAIN     = 'main',     '正式用例'
        TEARDOWN = 'teardown', '后置操作'

    role = models.CharField(
        '执行阶段', max_length=16,
        choices=Role.choices, default=Role.MAIN
    )
    order = models.PositiveIntegerField('执行顺序', default=0)
    enabled = models.BooleanField('是否启用', default=True)
    env_override = models.JSONField(
        '参数覆盖', null=True, blank=True,
        help_text='运行时覆盖用例参数，格式与 api_args 相同'
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True, null=True)

    class Meta:
        verbose_name = '套件用例项'
        verbose_name_plural = '套件用例项'
        ordering = ['order', 'id']
        # role 排序通过 get_case_api_items()/get_case_ui_items() 中的 annotate 实现
        # 同一套件内同一用例不能重复添加
        unique_together = []

    def __str__(self):
        case_name = (
            self.case_api.name if self.case_type == self.CaseType.API and self.case_api
            else (self.case_ui.name if self.case_ui else '未知')
        )
        return f"[{self.case_type}] {case_name} @ Suite({self.suite_id})"


class RunResult(models.Model):
    """ 执行结果 """
    objects: models.QuerySet

    class RunStatus(models.IntegerChoices):
        Init = 0, "初始化"
        Ready = 1, "准备开始"
        Running = 2, "正在执行"
        Reporting = 3, "正在生成报告"
        Done = 4, "执行完毕"
        Error = -1, "执行出错"

    class ScopeType(models.TextChoices):
        PROJECT = 'project', '项目'
        SPRINT = 'sprint', '迭代'

    suite = models.ForeignKey(Suite, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, null=True, blank=True, on_delete=models.SET_NULL)
    scope_type = models.CharField('执行域类型', max_length=16, choices=ScopeType.choices, default=ScopeType.PROJECT)
    scope_id = models.PositiveIntegerField('执行域ID', null=True, blank=True)
    product_line = models.ForeignKey(ProductLine, null=True, blank=True, on_delete=models.SET_NULL, related_name='run_results')
    trigger_source = models.CharField('触发来源', max_length=16, default='manual')
    execution_log = models.ForeignKey('SuiteExecutionLog', null=True, blank=True, on_delete=models.SET_NULL, related_name='run_results')
    snapshot_id = models.PositiveIntegerField('快照ID', null=True, blank=True)

    path = models.CharField("用例路径", max_length=255)
    is_pass = models.BooleanField("测试通过", default=False)
    status = models.IntegerField("执行状态", choices=RunStatus.choices, default=RunStatus.Init)
    created_at = models.DateTimeField("创建时间", auto_now_add=True, null=True)

# 性能测试模型（单独文件，通过此处导入保证被 Django 发现）
from .performance_models import PerformanceTest  # noqa


class DataSet(models.Model):
    """
    参数化数据集（DDT）。
    上传 CSV/Excel 后解析存储，执行用例/套件时传入 dataset_id 实现数据驱动。
    用例中用 ${参数名} 引用列名，引擎的 VarResolver 会自动替换。
    """
    objects: models.QuerySet

    name        = models.CharField('数据集名称', max_length=200)
    project     = models.ForeignKey(Project, on_delete=models.CASCADE,
                                    related_name='datasets', verbose_name='所属项目')
    columns     = models.JSONField('列名列表', default=list,
                                   help_text='CSV/Excel 第一行列名，如 ["username", "password"]')
    rows        = models.JSONField('数据行', default=list,
                                   help_text='二维数组，每行对应一组参数值')
    created_by  = models.ForeignKey(
        'auth.User', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='datasets', verbose_name='创建人'
    )
    created_at  = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at  = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '参数化数据集'
        verbose_name_plural = '参数化数据集'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({len(self.rows)} 行)'

    @property
    def row_count(self):
        return len(self.rows)

    def iter_rows(self):
        """生成 {列名: 值} 字典序列，供执行引擎逐行注入上下文"""
        for row in self.rows:
            yield dict(zip(self.columns, row))


class ExecutionSnapshot(models.Model):
    scope_type = models.CharField(max_length=16)
    scope_id = models.PositiveIntegerField()
    product_line = models.ForeignKey(ProductLine, null=True, blank=True, on_delete=models.SET_NULL, related_name='execution_snapshots')
    suite = models.ForeignKey(Suite, null=True, blank=True, on_delete=models.SET_NULL, related_name='execution_snapshots')
    suite_name = models.CharField(max_length=64, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']


class ExecutionCaseSnapshot(models.Model):
    snapshot = models.ForeignKey(ExecutionSnapshot, on_delete=models.CASCADE, related_name='case_snapshots')
    case_id = models.PositiveIntegerField()
    case_name = models.CharField(max_length=64)
    case_version = models.PositiveIntegerField(default=1)
    payload_json = models.JSONField(default=dict)

    class Meta:
        ordering = ['id']


class SuiteExecutionLog(models.Model):
    class StrategyType(models.TextChoices):
        MANUAL = 'manual', '手动执行'
        CRON = 'cron', '定时执行'
        WEBHOOK = 'webhook', 'Webhook'

    suite = models.ForeignKey(Suite, on_delete=models.CASCADE, related_name='execution_logs')
    strategy_type = models.CharField(max_length=16, choices=StrategyType.choices)
    strategy_key = models.CharField(max_length=255)
    strategy_label = models.CharField(max_length=255, blank=True, default='')
    strategy_payload = models.JSONField(default=dict, blank=True)
    execution_count = models.PositiveIntegerField(default=0)
    pass_count = models.PositiveIntegerField(default=0)
    fail_count = models.PositiveIntegerField(default=0)
    latest_result = models.ForeignKey(RunResult, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    latest_failed_result = models.ForeignKey(RunResult, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    recent_result_ids = models.JSONField(default=list, blank=True)
    first_triggered_at = models.DateTimeField(null=True, blank=True)
    last_triggered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-last_triggered_at', '-id']
        unique_together = [('suite', 'strategy_type', 'strategy_key')]

    @classmethod
    def record_run(cls, suite, result, trigger_source='manual'):
        now = timezone.now()
        if trigger_source == 'cron':
            strategy_type = cls.StrategyType.CRON
            strategy_key = suite.cron or 'cron'
            strategy_label = f'定时策略：{suite.cron or "未设置 Cron"}'
            strategy_payload = {'cron': suite.cron or ''}
        elif trigger_source == 'webhook':
            strategy_type = cls.StrategyType.WEBHOOK
            strategy_key = suite.hook_key or f'webhook:{suite.id}'
            strategy_label = 'Webhook 触发'
            strategy_payload = {'hook_key': suite.hook_key or ''}
        else:
            strategy_type = cls.StrategyType.MANUAL
            strategy_key = f'manual:{result.id}'
            strategy_label = '手动立即执行'
            strategy_payload = {}

        log, created = cls.objects.get_or_create(
            suite=suite,
            strategy_type=strategy_type,
            strategy_key=strategy_key,
            defaults={
                'strategy_label': strategy_label,
                'strategy_payload': strategy_payload,
                'execution_count': 0,
                'first_triggered_at': now,
            }
        )
        recent_ids = [result.id, *[rid for rid in (log.recent_result_ids or []) if rid != result.id]]
        is_pass = bool(result.status == RunResult.RunStatus.Done and result.is_pass)
        log.strategy_label = strategy_label
        log.strategy_payload = strategy_payload
        log.execution_count = (log.execution_count or 0) + 1
        log.pass_count = (log.pass_count or 0) + (1 if is_pass else 0)
        log.fail_count = (log.fail_count or 0) + (0 if is_pass else 1)
        log.latest_result = result
        if not is_pass:
            log.latest_failed_result = result
        if created or not log.first_triggered_at:
            log.first_triggered_at = now
        log.last_triggered_at = now
        log.recent_result_ids = recent_ids[:20]
        log.save(update_fields=['strategy_label', 'strategy_payload', 'execution_count', 'pass_count', 'fail_count', 'latest_result', 'latest_failed_result', 'first_triggered_at', 'last_triggered_at', 'recent_result_ids', 'updated_at'])
        if result.execution_log_id != log.id:
            result.execution_log = log
            result.save(update_fields=['execution_log'])
        return log


class ImportJob(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', '待处理'
        RUNNING = 'running', '处理中'
        SUCCESS = 'success', '成功'
        FAILED = 'failed', '失败'
        PARTIAL = 'partial', '部分成功'

    product_line = models.ForeignKey(ProductLine, null=True, blank=True, on_delete=models.SET_NULL, related_name='import_jobs')
    scope_type = models.CharField(max_length=16, blank=True, default='')
    scope_id = models.PositiveIntegerField(null=True, blank=True)
    file_path = models.CharField(max_length=512, blank=True, default='')
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    total = models.PositiveIntegerField(default=0)
    success = models.PositiveIntegerField(default=0)
    failed = models.PositiveIntegerField(default=0)
    error_file = models.CharField(max_length=512, blank=True, default='')
    detail = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='import_jobs')
    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-id']
