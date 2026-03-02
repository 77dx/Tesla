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
    users = models.ManyToManyField(
        User,
        through="User_Role",
        through_fields=('role', 'user'),
        related_name="roles",
        verbose_name="用户"
        )

    class Meta:
        verbose_name = "角色列表"
        verbose_name_plural = "角色列表"


class User_Role(models.Model):
    objects: models.QuerySet
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name="角色")
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "用户角色关系"
        verbose_name_plural = "用户角色关系"
        unique_together = ('user', 'role')   # 防止重复关系
















