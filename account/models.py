import os
import time

from django.db import models
from django.contrib.auth.models import User
from pathlib import Path
from system.models import Role

app_path = Path(__file__).parent
app_static_path = app_path / 'static'

def user_head_img_path(instance, filename):
    # ext = filename.split('.')[-1]
    filename = f"user_{instance.user.id}/{int(time.time())}_{filename}"
    return os.path.join("avatar", filename)
    # return f"{app_static_path}/use_{instance.user.id}/{int(time.time())}_{filename}"

class Avatar(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    avatar = models.FileField("用户头像", upload_to=user_head_img_path)

class Profile(models.Model):
    objects: models.QuerySet

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField("昵称", max_length=32, default="你是猪")
    avatar_url = models.CharField("头像地址", max_length=512)

    def get_role_list(self):
        role_list = Role.objects.filter(user=self.user)
        return role_list

    class Meta:
        verbose_name = "用户列表"
        verbose_name_plural = "用户列表"




