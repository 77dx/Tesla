"""
@ Title:
@ Author: Cathy
@ Time: 2024/12/5 15:49
"""
from django.conf.urls.static import static
from django.urls import path
from django.views.static import serve

from Tesla import settings
from .models import app_static_path
from .views import ProfileViewSet, UserProfileAdminViewSet
from rest_framework import routers


router = routers.SimpleRouter()
router.register('profile', ProfileViewSet, 'profile')
router.register('admin/users', UserProfileAdminViewSet, 'admin-users')

urlpatterns = [
    path("static/<path:path>/", serve, {"document_root": app_static_path})
]

urlpatterns += router.urls

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)