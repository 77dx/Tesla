from django.contrib.auth.models import User
from django.db import models
from system.models import Role


class ProductLine(models.Model):
    """产品线"""
    objects: models.QuerySet

    name = models.CharField('产品线名称', max_length=64, unique=True)
    description = models.CharField('描述', max_length=256, blank=True, default='')
    created_by = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='product_line_created',
        verbose_name='创建人'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True, null=True)
    updated_at = models.DateTimeField('修改时间', auto_now=True, null=True)

    class Meta:
        verbose_name = '产品线'
        verbose_name_plural = '产品线列表'
        ordering = ['id']

    def __str__(self):
        return self.name


class ProductLineMember(models.Model):
    """产品线成员（含该用户在此产品线的角色）"""
    objects: models.QuerySet

    product_line = models.ForeignKey(
        ProductLine,
        on_delete=models.CASCADE,
        related_name='members',
        verbose_name='产品线'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='product_line_memberships',
        verbose_name='用户'
    )
    role = models.ForeignKey(
        Role,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='product_line_members',
        verbose_name='角色（产品线级）'
    )
    joined_at = models.DateTimeField('加入时间', auto_now_add=True, null=True)

    class Meta:
        verbose_name = '产品线成员'
        verbose_name_plural = '产品线成员列表'
        unique_together = ('product_line', 'user')

    def __str__(self):
        return f'{self.product_line.name} - {self.user.username}'

    def get_permissions(self):
        """获取该成员在本产品线的权限码列表"""
        if not self.role:
            return []
        return list(self.role.permissions.values_list('code', flat=True))
