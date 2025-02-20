"""
@ Title:
@ Author: Cathy
@ Time: 2024/12/6 17:23
"""
from .views import DepartmentViewSet, PositionViewSet, RoleViewSet
from rest_framework import routers


router = routers.SimpleRouter()
router.register("department", DepartmentViewSet)
router.register("position", PositionViewSet)
router.register("role", RoleViewSet)

urlpatterns = router.urls