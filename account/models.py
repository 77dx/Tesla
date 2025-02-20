from django.db import models
from django.contrib.auth.models import User
from pathlib import Path
from system.models import Role

app_path = Path(__file__).parent
app_static_path = app_path / 'static'


def user_head_img_path(obj, filename):
    return f"{app_static_path}/user_{obj.id}/{filename}"


class Profile(models.Model):
    objects: models.QuerySet

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField("昵称", max_length=32, default="你是猪")
    avatar = models.FileField("用户头像", upload_to=user_head_img_path)

    def get_role_list(self):
        role_list = Role.objects.filter(user=self.user)
        return role_list




