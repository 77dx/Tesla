from django.db import models
from django.utils import timezone

from product_line.models import ProductLine
from project.models import Project
from suite.models import Environment


class AutomationProject(models.Model):
    class EngineType(models.TextChoices):
        PLAYWRIGHT = 'playwright', 'Playwright'

    name = models.CharField('项目名称', max_length=100)
    product_line = models.ForeignKey(ProductLine, on_delete=models.CASCADE, related_name='automation_projects')
    project = models.ForeignKey(Project, null=True, blank=True, on_delete=models.SET_NULL, related_name='automation_projects')
    engine_type = models.CharField('执行引擎', max_length=32, choices=EngineType.choices, default=EngineType.PLAYWRIGHT)
    repo_url = models.CharField('仓库地址', max_length=500, blank=True, default='')
    local_repo_path = models.CharField('本地仓库路径', max_length=500, blank=True, default='')
    default_branch = models.CharField('默认分支', max_length=100, blank=True, default='main')
    install_command = models.CharField('安装命令', max_length=500, blank=True, default='npm install')
    test_command = models.CharField('默认测试命令', max_length=500, blank=True, default='npx playwright test')
    report_dir = models.CharField('报告目录', max_length=255, blank=True, default='playwright-report')
    results_dir = models.CharField('结果目录', max_length=255, blank=True, default='test-results')
    created_by = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='automation_projects_created')
    updated_by = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='automation_projects_updated')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']
        unique_together = [('product_line', 'name')]

    def __str__(self):
        return self.name


class AutomationSuite(models.Model):
    automation_project = models.ForeignKey(AutomationProject, on_delete=models.CASCADE, related_name='suites')
    name = models.CharField('套件名称', max_length=100)
    suite_path = models.CharField('执行路径', max_length=255, blank=True, default='')
    command_override = models.CharField('自定义命令', max_length=500, blank=True, default='')
    tags = models.JSONField('标签', default=list, blank=True)
    enabled = models.BooleanField('是否启用', default=True)
    created_by = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='automation_suites_created')
    updated_by = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='automation_suites_updated')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']
        unique_together = [('automation_project', 'name')]

    def __str__(self):
        return self.name


class AutomationRun(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', '待执行'
        RUNNING = 'running', '执行中'
        PASSED = 'passed', '通过'
        FAILED = 'failed', '失败'
        ERROR = 'error', '异常'

    suite = models.ForeignKey(AutomationSuite, on_delete=models.CASCADE, related_name='runs')
    product_line = models.ForeignKey(ProductLine, on_delete=models.CASCADE, related_name='automation_runs')
    project = models.ForeignKey(Project, null=True, blank=True, on_delete=models.SET_NULL, related_name='automation_runs')
    environment = models.ForeignKey(Environment, null=True, blank=True, on_delete=models.SET_NULL, related_name='automation_runs')
    trigger_source = models.CharField('触发来源', max_length=32, default='manual')
    status = models.CharField('状态', max_length=16, choices=Status.choices, default=Status.PENDING)
    branch = models.CharField('分支', max_length=100, blank=True, default='')
    command = models.CharField('执行命令', max_length=500, blank=True, default='')
    base_url = models.CharField('Base URL', max_length=500, blank=True, default='')
    variables = models.JSONField('变量', default=dict, blank=True)
    workdir = models.CharField('工作目录', max_length=500, blank=True, default='')
    log_path = models.CharField('日志路径', max_length=500, blank=True, default='')
    report_path = models.CharField('报告路径', max_length=500, blank=True, default='')
    result_payload = models.JSONField('结果详情', default=dict, blank=True)
    created_by = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='automation_runs_created')
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-id']

    def mark_running(self):
        self.status = self.Status.RUNNING
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at'])

    def mark_finished(self, status, payload=None):
        self.status = status
        self.finished_at = timezone.now()
        if payload is not None:
            self.result_payload = payload
        self.save(update_fields=['status', 'finished_at', 'result_payload'])
