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
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    method = models.CharField("", max_length=8)
    url = models.CharField("", max_length=255)

    # 参数
    params = models.JSONField("查询字符串", blank=True, null=True, max_length=10240)   # 必须是json格式
    data = models.JSONField("表单参数", blank=True, null=True, max_length=10240)   # 必须是json格式
    json = models.JSONField("json参数", blank=True, null=True, max_length=10240)   # 必须是json格式
    cookies = models.JSONField("Cookies", blank=True, null=True, max_length=10240)   # 必须是json格式
    headers = models.JSONField("请求头", blank=True, null=True, max_length=10240)   # 必须是json格式

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

    # 生成yaml文件-对接apiframetest框架
    def to_yaml(self, path=None):
        from case_api.util import GenerateCase
        generator = GenerateCase(self.endpoint.id)
        return generator.to_yaml(path)

























