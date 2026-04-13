from os.path import exists
from random import random
from django.db import models
from ruamel.yaml import YAML
from Tesla import settings
from project.models import Project
from product_line.models import ProductLine

class Endpoint(models.Model):
    """接口"""
    objects: models.QuerySet
    name = models.CharField("接口名称", max_length=32)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    product_line = models.ForeignKey(
        ProductLine, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='endpoints', verbose_name='所属产品线'
    )
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
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="case_api", null=True, blank=True)
    product_line = models.ForeignKey(
        ProductLine, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='cases', verbose_name='所属产品线'
    )
    endpoint = models.ForeignKey(Endpoint, on_delete=models.CASCADE)
    alluer = models.JSONField("Allure标注", blank=True, null=True)
    # 关联迭代/需求（可选）
    sprint = models.ForeignKey(
        'project.Sprint', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='cases', verbose_name='所属迭代'
    )
    requirement = models.ForeignKey(
        'project.Requirement', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='cases', verbose_name='关联需求'
    )
    # 用例参数（实际传参）
    api_args = models.JSONField("接口用例参数", blank=True, null=True)
    version = models.PositiveIntegerField('版本号', default=1)
    # 用例脚本（可读写上下文变量）
    pre_script = models.TextField(
        "前置脚本", blank=True, default='',
        help_text='执行请求前运行的 Python 脚本，可通过 ctx 写入动态参数，例如: ctx["nonce"] = "123"'
    )
    post_script = models.TextField(
        "后置脚本", blank=True, default='',
        help_text='执行请求后运行的 Python 脚本，可读取 response_json/response_text 并写入 ctx'
    )
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


class CaseNode(models.Model):
    class NodeType(models.TextChoices):
        FOLDER = 'folder', '文件夹'
        CASE = 'case', '用例'

    name = models.CharField('名称', max_length=64)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    path = models.CharField('物化路径', max_length=255, default='/', db_index=True)
    node_type = models.CharField('节点类型', max_length=16, choices=NodeType.choices, default=NodeType.FOLDER)
    case = models.OneToOneField(Case, null=True, blank=True, on_delete=models.CASCADE, related_name='tree_node')
    order_no = models.PositiveIntegerField('排序', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        ordering = ['order_no', 'id']

    @classmethod
    def ensure_root(cls):
        root = cls.objects.filter(parent__isnull=True, node_type=cls.NodeType.FOLDER).order_by('id').first()
        if root:
            if root.path != '/':
                root.path = '/'
                root.save(update_fields=['path'])
            return root
        root = cls.objects.create(name='根目录', parent=None, path='/', node_type=cls.NodeType.FOLDER)
        return root



