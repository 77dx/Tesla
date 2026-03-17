"""
@ Title:
@ Author: Cathy
@ Time: 2024/12/6 17:23
"""
from .views import DepartmentViewSet, PositionViewSet, RoleViewSet, PermissionViewSet
from rest_framework import routers


router = routers.SimpleRouter()
router.register("department", DepartmentViewSet, "department")
router.register("position", PositionViewSet, "position")
router.register("role", RoleViewSet, "role")
router.register("permission", PermissionViewSet, "permission")

urlpatterns = router.urls