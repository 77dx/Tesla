"""
性能测试 - 配置与结果分离模型

PerformanceConfig  : 压测配置（可编辑，可重复执行）
PerformanceResult  : 每次执行的结果（只读，保留历史）
"""
from django.db import models
from .models import Suite
from project.models import Project


class PerformanceConfig(models.Model):
    """压测配置（可编辑，可多次执行）"""

    suite      = models.ForeignKey(Suite, on_delete=models.CASCADE,
                                   related_name='perf_configs', verbose_name='测试套件')
    project    = models.ForeignKey(Project, on_delete=models.CASCADE,
                                   related_name='perf_configs', verbose_name='所属项目')
    name       = models.CharField('压测名称', max_length=128, blank=True, default='',
                                  help_text='留空则展示套件名称')
    users      = models.PositiveIntegerField('并发用户数', default=10)
    spawn_rate = models.PositiveIntegerField('每秒启动用户数', default=1)
    run_time   = models.PositiveIntegerField('持续时间(秒)', default=60)
    host       = models.CharField('目标Host', max_length=255, blank=True, default='')
    case_ids   = models.JSONField('用例ID列表', blank=True, null=True)

    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    created_by = models.ForeignKey('auth.User', null=True, blank=True,
                                   on_delete=models.SET_NULL, related_name='+')

    class Meta:
        verbose_name = '压测配置'
        verbose_name_plural = '压测配置列表'
        ordering = ['-created_at']

    def __str__(self):
        return f'PerfConfig({self.id}) {self.name or self.suite.name}'

    @property
    def display_name(self):
        return self.name or self.suite.name

    @property
    def latest_result(self):
        return self.results.order_by('-created_at').first()


class PerformanceResult(models.Model):
    """每次压测执行的结果（不可修改，保留历史）"""

    class Status(models.TextChoices):
        PENDING = 'pending', '等待中'
        RUNNING = 'running', '执行中'
        DONE    = 'done',    '已完成'
        STOPPED = 'stopped', '已停止'
        ERROR   = 'error',   '执行出错'

    config     = models.ForeignKey(PerformanceConfig, on_delete=models.CASCADE,
                                   related_name='results', verbose_name='压测配置')

    # 执行时快照（配置可能之后被改，这里保存执行时的值）
    users      = models.PositiveIntegerField('并发用户数')
    spawn_rate = models.PositiveIntegerField('每秒启动用户数')
    run_time   = models.PositiveIntegerField('持续时间(秒)')
    host       = models.CharField('目标Host', max_length=255, blank=True, default='')

    # 执行状态
    status     = models.CharField('状态', max_length=16,
                                  choices=Status.choices, default=Status.PENDING)
    pid        = models.IntegerField('Locust PID', null=True, blank=True)
    work_dir   = models.CharField('工作目录', max_length=512, blank=True)
    error_msg  = models.TextField('错误信息', blank=True)

    # 结果数据
    summary    = models.JSONField('汇总统计', blank=True, null=True)
    stats_data = models.JSONField('时序统计', blank=True, null=True)

    created_at  = models.DateTimeField('创建时间', auto_now_add=True)
    started_at  = models.DateTimeField('开始时间', null=True, blank=True)
    finished_at = models.DateTimeField('结束时间', null=True, blank=True)
    created_by  = models.ForeignKey('auth.User', null=True, blank=True,
                                    on_delete=models.SET_NULL, related_name='+')

    class Meta:
        verbose_name = '压测结果'
        verbose_name_plural = '压测结果列表'
        ordering = ['-created_at']

    def __str__(self):
        return f'PerfResult({self.id}) config={self.config_id} status={self.status}'

    @property
    def duration(self):
        if self.started_at and self.finished_at:
            return (self.finished_at - self.started_at).total_seconds()
        return None
