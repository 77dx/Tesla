from django.contrib.auth.models import User
from django.db import models



class Project(models.Model):
    objects: models.QuerySet

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
    created_at = models.DateTimeField("创建时间", auto_now_add=True, null=True)
    updated_at = models.DateTimeField("修改时间", auto_now=True, null=True)
    updated_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="+", verbose_name="最后修改人")

class Config(models.Model):
    objects: models.QuerySet

    project = models.OneToOneField(Project, on_delete=models.CASCADE)
    conftest = models.TextField("pytest配置脚本", default="")
    created_at = models.DateTimeField("创建时间", auto_now_add=True, null=True)
    updated_at = models.DateTimeField("修改时间", auto_now=True, null=True)
    updated_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="+", verbose_name="最后修改人")