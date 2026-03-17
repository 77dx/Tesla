from django.contrib.auth.models import User
from django.db import models


# ==================== 权限 ====================

class Permission(models.Model):
    """权限码"""
    objects: models.QuerySet
    code = models.CharField("权限码", max_length=64, unique=True)
    name = models.CharField("权限名称", max_length=64)
    module = models.CharField("所属模块", max_length=32)

    class Meta:
        verbose_name = "权限"
        verbose_name_plural = "权限列表"
        ordering = ['module', 'code']

    def __str__(self):
        return f"{self.module} - {self.name}({self.code})"


# ==================== 部门 ====================

class Department(models.Model):
    objects: models.QuerySet
    name = models.CharField("部门名称", max_length=32)
    intro = models.CharField("部门简介", max_length=256, default="")
    leader = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default=None, related_name="led_departments", verbose_name="负责人")
    default_role = models.ForeignKey(
        "Role",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        related_name="default_for_departments",
        verbose_name="默认角色"
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True, null=True)

    class Meta:
        verbose_name = "部门"
        verbose_name_plural = "部门列表"

    def __str__(self):
        return self.name


# ==================== 职位 ====================

class Position(models.Model):
    objects: models.QuerySet
    name = models.CharField("职位名称", max_length=32)
    is_leader = models.BooleanField(verbose_name="负责人", default=False)
    created_at = models.DateTimeField("创建时间", auto_now_add=True, null=True)

    class Meta:
        verbose_name = "职位"
        verbose_name_plural = "职位列表"

    def __str__(self):
        return self.name


# ==================== 角色 ====================

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
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name="roles",
        verbose_name="权限"
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True, null=True)

    class Meta:
        verbose_name = "角色列表"
        verbose_name_plural = "角色列表"

    def __str__(self):
        return self.name


class User_Role(models.Model):
    objects: models.QuerySet
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name="角色")
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "用户角色关系"
        verbose_name_plural = "用户角色关系"
        unique_together = ('user', 'role')
