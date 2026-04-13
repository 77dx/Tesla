"""
性能测试模型
"""
from django.db import models
from .models import Suite
from project.models import Project


class PerformanceTest(models.Model):
    """性能测试记录"""

    class Status(models.TextChoices):
        PENDING  = 'pending',  '等待中'
        RUNNING  = 'running',  '执行中'
        DONE     = 'done',     '已完成'
        STOPPED  = 'stopped',  '已停止'
        ERROR    = 'error',    '执行出错'

    suite        = models.ForeignKey(Suite, on_delete=models.CASCADE,
                                     related_name='performance_tests', verbose_name='测试套件')
    project      = models.ForeignKey(Project, on_delete=models.CASCADE,
                                     related_name='performance_tests', verbose_name='所属项目')

    # ── 压测配置 ──────────────────────────────────────────────
    name         = models.CharField('压测名称', max_length=128, blank=True, default='',
                                    help_text='自定义名称，留空则展示套件名称')
    users        = models.PositiveIntegerField('并发用户数', default=10)
    spawn_rate   = models.PositiveIntegerField('每秒启动用户数', default=1)
    run_time     = models.PositiveIntegerField('持续时间(秒)', default=60)
    host         = models.CharField('目标Host', max_length=255, blank=True, default='',
                                    help_text='如 https://api.example.com，留空则从环境配置读取')
    case_ids     = models.JSONField('用例ID列表', blank=True, null=True,
                                    help_text='指定要压测的用例，为空则使用套件全部用例')

    # ── 执行状态 ──────────────────────────────────────────────
    status       = models.CharField('状态', max_length=16,
                                    choices=Status.choices, default=Status.PENDING)
    pid          = models.IntegerField('Locust 进程 PID', null=True, blank=True)
    work_dir     = models.CharField('工作目录', max_length=512, blank=True)
    error_msg    = models.TextField('错误信息', blank=True)

    # ── 汇总结果 ──────────────────────────────────────────────
    summary      = models.JSONField('汇总统计', blank=True, null=True,
                                    help_text='{\'total_requests\': N, \'failure_rate\': 0.02, \'avg_response_time\': 120, ...}')
    stats_data   = models.JSONField('详细统计数据（时序）', blank=True, null=True,
                                    help_text='[{ts, rps, avg_rt, failures}, ...]')

    created_at   = models.DateTimeField('创建时间', auto_now_add=True)
    started_at   = models.DateTimeField('开始时间', null=True, blank=True)
    finished_at  = models.DateTimeField('结束时间', null=True, blank=True)
    created_by   = models.ForeignKey('auth.User', null=True, blank=True,
                                     on_delete=models.SET_NULL, related_name='+')

    class Meta:
        verbose_name = '性能测试'
        verbose_name_plural = '性能测试列表'
        ordering = ['-created_at']

    def __str__(self):
        return f'PerformanceTest({self.id}) suite={self.suite_id} status={self.status}'

    @property
    def duration(self):
        if self.started_at and self.finished_at:
            return (self.finished_at - self.started_at).total_seconds()
        return None
