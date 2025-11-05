from django.contrib import admin
from .models import Profile, Avatar


@admin.register(Profile)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['id','user_id', 'nickname', 'avatar_url']

@admin.register(Avatar)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'avatar']

