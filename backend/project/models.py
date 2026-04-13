from django.contrib.auth.models import User
from django.db import models



class Project(models.Model):
    objects: models.QuerySet

    class Status(models.TextChoices):
        PLANNING = 'planning', '规划中'
        ACTIVE   = 'active',   '进行中'
        TESTING  = 'testing',  '测试中'
        DONE     = 'done',     '已完成'
        ARCHIVED = 'archived', '已归档'

    class Priority(models.IntegerChoices):
        NORMAL  = 0, '普通'
        IMPORTANT = 1, '重要'
        URGENT  = 2, '紧急'

    name = models.CharField("项目名称", max_length=32)
    intro = models.CharField("项目简介", max_length=256, default="")
    url = models.CharField("项目地址", max_length=256, default="")
    members = models.ManyToManyField(User, blank=True, related_name="project_set")
    pm = models.ForeignKey(User, null=True, on_delete=models.SET_DEFAULT, default=1, related_name="project_pm_list")
    product_line = models.ForeignKey(
        'product_line.ProductLine',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='projects',
        verbose_name='所属产品线'
    )
    status     = models.CharField('状态', max_length=20,
                                  choices=Status.choices, default=Status.PLANNING)
    priority   = models.SmallIntegerField('优先级', choices=Priority.choices, default=Priority.NORMAL)
    start_date = models.DateField('开始日期', null=True, blank=True)
    end_date   = models.DateField('结束日期', null=True, blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True, null=True)
    updated_at = models.DateTimeField("修改时间", auto_now=True, null=True)
    updated_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="+", verbose_name="最后修改人")

    class Meta:
        verbose_name = '项目'
        verbose_name_plural = '项目'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Sprint(models.Model):
    """迭代/版本，支持独立于项目存在（产品线维度）"""
    objects: models.QuerySet

    class Status(models.TextChoices):
        PLANNING  = 'planning',  '规划中'
        ACTIVE    = 'active',    '进行中'
        REVIEWING = 'reviewing', '评审中'
        DONE      = 'done',      '已完成'

    project    = models.ForeignKey(Project, on_delete=models.SET_NULL,
                                   null=True, blank=True,
                                   related_name='sprints', verbose_name='所属项目')
    product_line = models.ForeignKey(
        'product_line.ProductLine',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='sprints',
        verbose_name='所属产品线'
    )
    name       = models.CharField('迭代名称', max_length=64,
                                  help_text='如：Sprint 2024-Q1、v2.5.0')
    goal       = models.TextField('迭代目标', blank=True, default='')
    status     = models.CharField('状态', max_length=20,
                                  choices=Status.choices, default=Status.PLANNING)
    start_date = models.DateField('开始日期', null=True, blank=True)
    end_date   = models.DateField('结束日期', null=True, blank=True)
    created_by = models.ForeignKey('auth.User', null=True, blank=True,
                                   on_delete=models.SET_NULL, related_name='+',
                                   verbose_name='创建人')
    owner = models.ForeignKey('auth.User', null=True, blank=True,
                              on_delete=models.SET_NULL, related_name='owned_sprints',
                              verbose_name='迭代负责人')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    updated_by = models.ForeignKey('auth.User', null=True, blank=True,
                                   on_delete=models.SET_NULL, related_name='+',
                                   verbose_name='最后操作人')

    class Meta:
        verbose_name = '迭代'
        verbose_name_plural = '迭代'
        ordering = ['-start_date', '-id']

    def __str__(self):
        if self.project:
            return f'{self.project.name} / {self.name}'
        return self.name

    @property
    def is_overdue(self):
        from django.utils import timezone
        return bool(
            self.end_date and self.status != 'done'
            and self.end_date < timezone.now().date()
        )


class Requirement(models.Model):
    """需求/Story，拆分自迭代，有独立状态和优先级"""
    objects: models.QuerySet

    class Status(models.TextChoices):
        TODO      = 'todo',      '待开发'
        IN_DEV    = 'in_dev',    '开发中'
        IN_TEST   = 'in_test',   '测试中'
        IN_REVIEW = 'in_review', '评审中'
        DONE      = 'done',      '已完成'
        REJECTED  = 'rejected',  '已驳回'

    class Priority(models.IntegerChoices):
        LOW    = 0, '低'
        MEDIUM = 1, '中'
        HIGH   = 2, '高'
        URGENT = 3, '紧急'

    sprint     = models.ForeignKey(Sprint, on_delete=models.CASCADE,
                                   related_name='requirements', verbose_name='所属迭代')
    title      = models.CharField('需求标题', max_length=200)
    desc       = models.TextField('需求描述', blank=True, default='')
    status     = models.CharField('状态', max_length=20,
                                  choices=Status.choices, default=Status.TODO)
    priority   = models.SmallIntegerField('优先级',
                                          choices=Priority.choices, default=Priority.MEDIUM)
    assignee   = models.ForeignKey('auth.User', null=True, blank=True,
                                   on_delete=models.SET_NULL,
                                   related_name='requirements', verbose_name='负责人')
    start_date = models.DateField('开始日期', null=True, blank=True)
    due_date   = models.DateField('截止日期', null=True, blank=True)
    estimate   = models.SmallIntegerField('预估工时(h)', default=0)
    created_by = models.ForeignKey('auth.User', null=True, blank=True,
                                   on_delete=models.SET_NULL, related_name='+',
                                   verbose_name='创建人')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '需求'
        verbose_name_plural = '需求'
        ordering = ['-priority', 'due_date']

    def __str__(self):
        return self.title


class Config(models.Model):
    objects: models.QuerySet

    project = models.OneToOneField(Project, on_delete=models.CASCADE)
    conftest = models.TextField("pytest配置脚本", default="")
    created_at = models.DateTimeField("创建时间", auto_now_add=True, null=True)
    updated_at = models.DateTimeField("修改时间", auto_now=True, null=True)
    updated_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="+", verbose_name="最后修改人")


class ProjectCaseRef(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='case_refs')
    case = models.ForeignKey('case_api.Case', on_delete=models.CASCADE, related_name='project_refs')
    enabled = models.BooleanField(default=True)
    priority = models.SmallIntegerField(default=0)
    tags = models.JSONField(default=list, blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('project', 'case')]
        ordering = ['-id']


class ProjectSuiteRef(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='suite_refs')
    suite = models.ForeignKey('suite.Suite', on_delete=models.CASCADE, related_name='project_refs')
    enabled = models.BooleanField(default=True)
    priority = models.SmallIntegerField(default=0)
    tags = models.JSONField(default=list, blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('project', 'suite')]
        ordering = ['-id']


class SprintCaseRef(models.Model):
    sprint = models.ForeignKey(Sprint, on_delete=models.CASCADE, related_name='case_refs')
    case = models.ForeignKey('case_api.Case', on_delete=models.CASCADE, related_name='sprint_refs')
    enabled = models.BooleanField(default=True)
    priority = models.SmallIntegerField(default=0)
    tags = models.JSONField(default=list, blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('sprint', 'case')]
        ordering = ['-id']


class SprintSuiteRef(models.Model):
    sprint = models.ForeignKey(Sprint, on_delete=models.CASCADE, related_name='suite_refs')
    suite = models.ForeignKey('suite.Suite', on_delete=models.CASCADE, related_name='sprint_refs')
    enabled = models.BooleanField(default=True)
    priority = models.SmallIntegerField(default=0)
    tags = models.JSONField(default=list, blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('sprint', 'suite')]
        ordering = ['-id']