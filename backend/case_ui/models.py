from django.db import models
from selenium.webdriver.common.by import By

from product_line.models import ProductLine
from project.models import Project

by_list = []
for attr in dir(By):
    if attr.startswith('_') or attr.islower():
        continue
    by_list.append((attr, attr))


class Element(models.Model):
    objects: models.QuerySet

    name = models.CharField('元素名称', max_length=32)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    by = models.CharField('定位方式', choices=by_list, default='XPATH', max_length=20)
    value = models.CharField('定位表达式', max_length=255)
    created_at = models.DateTimeField('创建时间', auto_now_add=True, null=True)


class Case(models.Model):
    objects: models.QuerySet

    class Platform(models.TextChoices):
        WEB = 'web', 'Web'
        APP = 'app', 'App'

    name = models.CharField('用例名称', max_length=255)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='case_ui', null=True, blank=True)
    product_line = models.ForeignKey(ProductLine, on_delete=models.SET_NULL, null=True, blank=True, related_name='ui_cases', verbose_name='所属产品线')
    sprint = models.ForeignKey('project.Sprint', null=True, blank=True, on_delete=models.SET_NULL, related_name='ui_cases', verbose_name='所属迭代')
    requirement = models.ForeignKey('project.Requirement', null=True, blank=True, on_delete=models.SET_NULL, related_name='ui_cases', verbose_name='关联需求')
    platform = models.CharField('平台类型', max_length=16, choices=Platform.choices, default=Platform.WEB)
    entry_url = models.CharField('入口地址', max_length=255, blank=True, default='')
    usefixtures = models.JSONField('fixture列表', blank=True, null=True, default=list)
    steps = models.JSONField('用例步骤', blank=True, null=True, default=list)
    validate = models.JSONField('断言规则', blank=True, null=True, default=list)
    extract = models.JSONField('数据提取', blank=True, null=True, default=list)
    pre_script = models.TextField('前置脚本', blank=True, default='')
    post_script = models.TextField('后置脚本', blank=True, default='')
    version = models.PositiveIntegerField('版本号', default=1)
    created_at = models.DateTimeField('创建时间', auto_now_add=True, null=True)
    updated_at = models.DateTimeField('修改时间', auto_now=True, null=True)
    created_by = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='case_ui_created', verbose_name='创建人')
    updated_by = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='case_ui_updated', verbose_name='最后修改人')

    def to_xlsx(self, path):
        import openpyxl
        from openpyxl.worksheet.worksheet import Worksheet
        from .serializers import CaseUISerializer

        serializer = CaseUISerializer(self)
        json_data = serializer.data
        xlsx_data = []
        xlsx_data.append(['步骤', '步骤名', '关键字', '参数'])
        xlsx_data.append(['-1', '用例名称', 'name', json_data['name']])
        xlsx_data.append(['-1', '声明fixture', 'mark', 'usefixtures', ','.join(json_data.get('usefixtures') or [])])
        for step in json_data.get('steps') or []:
            _blank = step.pop('_BlankField', []) if isinstance(step, dict) else []
            fields = list(step.values()) if isinstance(step, dict) else [step]
            fields.extend(_blank)
            xlsx_data.append(fields)
        wb = openpyxl.Workbook()
        ws: Worksheet = wb.active
        for d in xlsx_data:
            ws.append(d)
        wb.save(path / f'test_{self.name}_{self.id}.xlsx')


class CaseRunHistory(models.Model):
    objects: models.QuerySet

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='run_histories', verbose_name='UI用例')
    environment = models.ForeignKey('suite.Environment', null=True, blank=True, on_delete=models.SET_NULL, related_name='ui_case_histories', verbose_name='运行环境')
    success = models.BooleanField('是否成功', default=False)
    error = models.TextField('错误信息', blank=True, default='')
    duration = models.FloatField('耗时(秒)', default=0)
    retry_count = models.PositiveIntegerField('重试次数', default=0)
    assertions = models.JSONField('断言结果', blank=True, null=True, default=list)
    extracted = models.JSONField('提取结果', blank=True, null=True, default=dict)
    screenshots = models.JSONField('截图列表', blank=True, null=True, default=list)
    execution_logs = models.JSONField('执行日志', blank=True, null=True, default=list)
    created_by = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='ui_case_run_histories', verbose_name='执行人')
    created_at = models.DateTimeField('执行时间', auto_now_add=True, null=True)

    class Meta:
        ordering = ['-id']
