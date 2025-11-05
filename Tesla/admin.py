"""
@ Title:
@ Author: Cathy
@ Time: 2025/4/17 15:18
"""
from django.contrib import admin
from beifan.admin import FeedBackAdmin
from beifan.models import FeedBack

admin.site.site_header = "鱼小七自动化测试系统"
admin.site.site_title = "鱼小七"
admin.site.index_title = "功能模块"
