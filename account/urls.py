"""
@ Title:
@ Author: Cathy
@ Time: 2024/12/5 15:49
"""
from django.urls import path
from django.views.static import serve

from .models import app_static_path
from .views import ProfileViewSet
from rest_framework import routers


router = routers.SimpleRouter()
router.register('profile', ProfileViewSet, 'profile')

urlpatterns = [
    path("static/<path:path>", serve, {"document_root": app_static_path})
]

urlpatterns += router.urls
