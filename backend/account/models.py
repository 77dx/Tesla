import os
import time

from django.db import models
from django.contrib.auth.models import User
from pathlib import Path
from system.models import Role, Department, Position

app_path = Path(__file__).parent
app_static_path = app_path / 'static'

def user_head_img_path(instance, filename):
    filename = f"user_{instance.user.id}/{int(time.time())}_{filename}"
    return os.path.join("avatar", filename)


class Avatar(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    avatar = models.FileField("用户头像", upload_to=user_head_img_path)
    created_at = models.DateTimeField("创建时间", auto_now_add=True, null=True)


class Profile(models.Model):
    objects: models.QuerySet

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField("昵称", max_length=32, default="你是猪")
    avatar_url = models.CharField("头像地址", max_length=512, default="")
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        related_name="members",
        verbose_name="所属部门"
    )
    position = models.ForeignKey(
        Position,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        related_name="members",
        verbose_name="职位"
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True, null=True)

    def get_role_list(self):
        return Role.objects.filter(users=self.user)

    def save(self, *args, **kwargs):
        # 检测部门是否发生变化，自动同步 default_role
        if self.pk:
            try:
                old = Profile.objects.select_related('department').get(pk=self.pk)
                old_dept = old.department
                new_dept = self.department

                if old_dept != new_dept:
                    # 移除旧部门的 default_role（如果有且用户拥有该角色）
                    if old_dept and old_dept.default_role:
                        self.user.roles.remove(old_dept.default_role)
                    # 添加新部门的 default_role（如果有且用户尚未拥有该角色）
                    if new_dept and new_dept.default_role:
                        self.user.roles.add(new_dept.default_role)
            except Profile.DoesNotExist:
                pass
        else:
            # 首次创建：保存后再处理角色（在 super().save() 之后执行）
            super().save(*args, **kwargs)
            if self.department and self.department.default_role:
                self.user.roles.add(self.department.default_role)
            return

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "用户列表"
        verbose_name_plural = "用户列表"
