from django.db import models
from django.contrib.auth.models import User, Group, Permission
import datetime

# 给beifan的app创建用户组
# beifan_group = Group.objects.create(name="Beifan Members")
# 分配权限
# permission = Permission.objects.get(codename="view_resource")
# beifan_group.permissions.add(permission)


# 评价表
class FeedBack(models.Model):
    quality = models.IntegerField("商品质量", default=1)
    attitude = models.IntegerField("客服态度", default=1)
    speed = models.IntegerField("物流速度", default=1)
    text = models.TextField("意见反馈", max_length=150, default="")
    anonymous = models.BooleanField("是否匿名", default=True)
    # 外键
    user = models.ForeignKey(User, default=1, on_delete=models.CASCADE, verbose_name="用户名")

    # 修改数据时，页面顶部显示数据的id
    def __str__(self):
        return "ID: %s" % self.pk

    class Meta:
        db_table = "feedback"
        # 前面加-表示降序，不加为正序
        ordering = ["-id"]
        verbose_name = "评价列表"
        verbose_name_plural = "评价列表"


# 暂时不用，先用了django的user
class MyUser(models.Model):
    username = models.CharField("用户名", max_length=100)
    password = models.CharField("密码", max_length=100)
    email = models.CharField("邮箱", max_length=100)
    create_time = models.DateTimeField("注册时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        db_table = "myuser"

