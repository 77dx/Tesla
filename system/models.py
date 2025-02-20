from django.contrib.auth.models import User
from django.db import models


class Department(models.Model):
    objects: models.QuerySet
    name = models.CharField("部门名称", max_length=32)
    intro = models.CharField("部门简介", max_length=256, default="")
    leader = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default=None)


class Position(models.Model):
    objects: models.QuerySet
    name = models.CharField("职位名称", max_length=32)
    is_leader = models.BooleanField(verbose_name="负责人", default=False)


class Role(models.Model):
    objects: models.QuerySet
    name = models.CharField("角色名称", max_length=32, default="未命名")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)























