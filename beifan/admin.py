from django.contrib import admin
from django.contrib.auth.models import User
from .models import FeedBack
import re


# 在admin后台注册feedback这个model
@admin.register(FeedBack)
class FeedBackAdmin(admin.ModelAdmin):
    # 后台列表显示的字段
    list_display = ["id", "quality", "attitude", "speed", "text", "anonymous", "user"]
    # 修改后台详情页字段的顺序(要所有字段都写上，不然就不显示了)
    fields = ["quality", "attitude", "speed", "text", "anonymous", "user"]
    # 搜索框
    search_fields = ['id', 'user']
    # 列表分页
    list_per_page = 10
    # 查询模型的数据信息，用于展示在admin的数据列表页
    def get_queryset(self, request):
        return super().get_queryset(request)
    # 改变非外键字段的下拉框数据
    def formfield_for_choice_field(self, db_field, request, **kwargs):
        ...
    # 在新增或者修改数据时，点击保存按钮触发
    def save_model(self, request, obj, form, change):
        return super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    # 在新增和修改数据时，外键的用户名字段没有过滤，此处的逻辑还是不符合需求
    # 这本书中只是筛选了第一位的用户进行填充，没有关联到当前登录的用户，下面自己进行了修改，但是修改的时候可以，新增报错了，因为
    # 所取的url的信息并不存在，导致报错。
    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == 'user':
    #         if not request.user.is_superuser:
    #             v = FeedBack.objects.filter(id__lt=2)
    #             kwargs['queryset'] = User.objects.filter(id__in=v)
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # 这个只是处理了在修改数据时，外键用户字段只取改数据的创建人，但是在新增数据时，此处时报错的。
        # url = request.get_full_path()
        # feedback_id = int(re.findall('\d+', url)[0])
        # if db_field.name == 'user':
        #     login_user = request.user
        #     if not login_user.is_superuser:
        #         pub_user_id = FeedBack.objects.filter(id=feedback_id)[0].user_id
        #         kwargs['queryset'] = User.objects.filter(id=pub_user_id)
        # return super().formfield_for_foreignkey(db_field, request, **kwargs)
