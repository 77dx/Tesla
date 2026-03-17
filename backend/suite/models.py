import logging
import time
from pathlib import Path
from django.db import models
from django_q.humanhash import uuid
from django_q.models import Schedule
from django_q.tasks import schedule
from project.models import Project
from case_api.models import Case as CaseAPI
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
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
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
    hook_key = models.CharField("webhook密钥", max_length=255, blank=True)
    schedule = models.ForeignKey(Schedule, null=True, blank=True, on_delete=models.SET_NULL)
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

    def save(self, *args, **kwargs):
        if self.run_type == self.RunType.CRON and self.cron:
            try:
                self.schedule = schedule(
                    'suite.tasks.run_by_cron_task', self.id,
                    cron=self.cron, schedule_type="C"
                )
            except ImportError:
                logger.warning("croniter not installed, skipping schedule creation")
                if self.schedule:
                    self.schedule.delete()
                    self.schedule = None
        else:
            if self.schedule:
                self.schedule.delete()
                self.schedule = None

        if self.run_type == self.RunType.WebHook:
            if not self.hook_key:
                self.hook_key = uuid()[0]
        return super().save(*args, **kwargs)

    def run(self, case_ids=None, ui_case_ids=None, initial_context=None):
        """
        执行测试套件。

        执行粒度：SuiteCaseItem（用例粒度），而非接口粒度。

        参数:
            case_ids: 指定要执行的 CaseAPI id 列表（None 表示取套件内全部已启用 API 用例）
            ui_case_ids: 指定要执行的 CaseUI id 列表（None 表示取套件内全部已启用 UI 用例）
            initial_context: 初始上下文字典

        Returns:
            RunResult 对象
        """
        from Tesla import settings

        # 1. 创建执行记录
        result: RunResult = RunResult.objects.create(
            suite=self,
            project=self.project,
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

        # 3. 确定本次要执行的 API 用例 id 列表
        if case_ids is not None:
            if isinstance(case_ids, str):
                case_ids = [int(x.strip()) for x in case_ids.split(',') if x.strip()]
            elif isinstance(case_ids, int):
                case_ids = [case_ids]
            api_case_ids = [int(x) for x in case_ids]
        else:
            api_case_ids = list(
                self.get_case_api_items()
                .values_list('case_api_id', flat=True)
            )

        # 4. 确定本次要执行的 UI 用例 id 列表
        if ui_case_ids is not None:
            if isinstance(ui_case_ids, str):
                ui_case_ids = [int(x.strip()) for x in ui_case_ids.split(',') if x.strip()]
            elif isinstance(ui_case_ids, int):
                ui_case_ids = [ui_case_ids]
            ui_ids = [int(x) for x in ui_case_ids]
        else:
            ui_ids = list(
                self.get_case_ui_items()
                .values_list('case_ui_id', flat=True)
            )

        # 5. 生成 UI 测试用例文件
        for case_ui in CaseUI.objects.filter(id__in=ui_ids):
            case_ui.to_xlsx(path)

        # 6. 提交 Celery 任务（新版 v2.0：直接调用 SuiteRunner，不再生成 YAML/调用 pytest）
        if api_case_ids:
            from suite.tasks import run_suite_task
            run_suite_task.delay(
                result.id, api_case_ids, initial_context or {},
                max_retries=self.retry_count,
                retry_delay=self.retry_delay,
                timeout_seconds=self.timeout_seconds,
                fail_strategy=self.fail_strategy,
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

    suite = models.ForeignKey(Suite, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    path = models.CharField("用例路径", max_length=255)
    is_pass = models.BooleanField("测试通过", default=False)
    status = models.IntegerField("执行状态", choices=RunStatus.choices, default=RunStatus.Init)
    created_at = models.DateTimeField("创建时间", auto_now_add=True, null=True)
