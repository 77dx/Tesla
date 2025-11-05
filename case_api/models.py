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

    # 生成yaml文件
    def to_yaml(self):
        """将数据库数据转换成yaml并保存"""
        # 查询接口的ddt用例
        case_data_list = Case.objects.filter(endpoint_id=self.endpoint)
        # 查询cased对应的endpoint
        endpoint = Endpoint.objects.get(pk=self.endpoint)
        # api框架的数据格式
        yaml_data = {"feature": "", "story": "", "title": "", "request":
            {"url": "", "method": "", "headers": {}}, "parametrize": [], "extract": {},
                     "validate": {}}
        # feature--项目
        yaml_data["feature"] = Project.objects.get(id=endpoint.project_id).name
        # story--接口
        yaml_data["story"] = endpoint.name
        # title--用例name(ddt的用例名称未实现)
        yaml_data["title"] = endpoint.name
        # request
        yaml_data["request"]["method"] = endpoint.method
        yaml_data["request"]["url"] = endpoint.url
        yaml_data["request"]["headers"] = endpoint.headers
        # 处理request中data部分
        keys_list = []
        values_list = []
        data_type = ""
        for case in case_data_list:
            # extract
            if case.extract:
                yaml_data["extract"] = case.extract
            # validate
            yaml_data["validate"] = case.validate

            for key in ['params', 'data', 'json', 'files']:
                value = case.api_args.get(key)
                if value not in [None, '', {}, []]:
                    yaml_data["request"][key] = value
                    data_type = key
            keys_list = [key for key in yaml_data["request"][data_type].keys()]
            value_list = []
            for value in yaml_data["request"][data_type].values():
                l = []
                if len(l) < 2:
                    l.append(value)
                value_list.extend(l)
            values_list.append(value_list)

        parametrize = []
        parametrize.append(keys_list)
        parametrize.extend(values_list)
        for key in keys_list:
            yaml_data["request"][data_type][key] = '$ddt{' + key + '}'

        yaml_data["parametrize"] = parametrize

        # 写入yaml文件
        yaml = YAML()
        yaml.representer.ignore_aliases = lambda *data: True  # 关键配置：禁用锚点
        # yaml.indent(sequence=4, offset=2)
        # yaml.default_flow_style = False
        file_path = f"{settings.TEST_YAML_PATH}/{endpoint.name}_{random.randint(0, 9999)}.yaml"
        with open(file_path, 'w', encoding="utf-8") as f:
            yaml.dump([yaml_data], f)
        if exists(file_path):
            return True
        return False

























