from os.path import exists
from random import random
from django.db import models
from ruamel.yaml import YAML
from Tesla import settings
from project.models import Project

class Endpoint(models.Model):
    """接口"""
    objects: models.QuerySet
    name = models.CharField("接口名称", max_length=32)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    method = models.CharField("", max_length=8)
    url = models.CharField("", max_length=255)
    service_key = models.CharField(
        '服务标识',
        max_length=64, blank=True, default='',
        help_text='对应环境 urls 列表中的 var 字段（如 user-site），执行时从环境中匹配 base URL'
    )

    # 参数
    params = models.JSONField("查询字符串", blank=True, null=True, max_length=10240)   # 必须是json格式
    data = models.JSONField("表单参数", blank=True, null=True, max_length=10240)   # 必须是json格式
    json = models.JSONField("json参数", blank=True, null=True, max_length=10240)   # 必须是json格式
    cookies = models.JSONField("Cookies", blank=True, null=True, max_length=10240)   # 必须是json格式
    headers = models.JSONField("请求头", blank=True, null=True, max_length=10240)   # 必须是json格式

    # ==================== 依赖驱动执行(DAG) ====================
    # requires: 当前接口执行前必须存在的上下文变量列表
    # provides: 当前接口执行后会写入上下文的变量列表(通常来自 extract)
    #
    # 这些字段用于 suite 模块在“非顺序执行”模式下自动构建依赖图并并行调度。
    requires = models.JSONField("依赖变量", blank=True, null=True)
    provides = models.JSONField("产出变量", blank=True, null=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True, null=True)
    updated_at = models.DateTimeField("修改时间", auto_now=True, null=True)
    created_by = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.SET_NULL, related_name="endpoint_created", verbose_name="创建人")
    updated_by = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.SET_NULL, related_name="+", verbose_name="最后修改人")

class Case(models.Model):
    objects: models.QuerySet
    # 接口用例
    name = models.CharField("用例名称", max_length=32)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="case_api")
    endpoint = models.ForeignKey(Endpoint, on_delete=models.CASCADE)
    alluer = models.JSONField("Allure标注", blank=True, null=True)
    # 用例参数（实际传参）
    api_args = models.JSONField("接口用例参数", blank=True, null=True)
    # 数据提取
    extract = models.JSONField("数据提取", blank=True, null=True)
    # 断言
    validate = models.JSONField("断言")
    created_at = models.DateTimeField("创建时间", auto_now_add=True, null=True)
    updated_at = models.DateTimeField("修改时间", auto_now=True, null=True)
    created_by = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.SET_NULL, related_name="case_api_created", verbose_name="创建人")
    updated_by = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.SET_NULL, related_name="+", verbose_name="最后修改人")

    # 生成yaml文件-对接apiframetest框架
    def to_yaml(self, path=None):
        from case_api.util import GenerateCase
        generator = GenerateCase(self.endpoint.id)
        return generator.to_yaml(path)

























