"""
@ Title:
@ Author: Cathy
@ Time: 2024/12/9 14:17
"""
from .views import ProjectViewSet, ConfigViewSet
from rest_framework import routers


router = routers.SimpleRouter()
router.register("project", ProjectViewSet)
router.register("config", ConfigViewSet)


urlpatterns = router.urls