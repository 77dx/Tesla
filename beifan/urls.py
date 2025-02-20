"""
@ Title:
@ Author: Cathy
@ Time: 2024/10/8 11:44
"""
from django.urls import path, include
from . import views
from django.views.generic import TemplateView
from rest_framework import routers

urlpatterns = [
    # path("", views.index),
    path("", TemplateView.as_view(template_name="beifan/register.html")),  # 路由直接配置html页面
    path("register", views.register),
    path("login", views.token_login),
    path("hello", views.hello),
    path("rating", views.rating),
    path("time", views.current_datetime),
    path("my_view", views.my_view),

]

router = routers.SimpleRouter()
router.register('feedback', views.FeedBackViewsSet)
router.register('user', views.UserViewSet)

urlpatterns += router.urls