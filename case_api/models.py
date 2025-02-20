from django.db import models

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
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    endpoint = models.ForeignKey(Endpoint, on_delete=models.CASCADE)

    alluer = models.JSONField("Allure标注", blank=True, null=True)
    # 用例参数（实际传参）
    api_args = models.JSONField("接口用例参数", blank=True, null=True)
    # 数据提取
    extract = models.JSONField("数据提取", blank=True, null=True)
    # 断言
    validate = models.JSONField("断言")

    # 生成yaml文件





















