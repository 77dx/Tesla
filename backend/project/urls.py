"""
@ Title:
@ Author: Cathy
@ Time: 2024/12/9 14:17
"""
from .views import (
    ProjectViewSet, ConfigViewSet, SprintViewSet, RequirementViewSet,
    ProjectCaseRefViewSet, ProjectSuiteRefViewSet, SprintCaseRefViewSet, SprintSuiteRefViewSet,
)
from rest_framework import routers


router = routers.SimpleRouter()
router.register("project", ProjectViewSet)
router.register("config", ConfigViewSet)
router.register("sprint", SprintViewSet)
router.register("requirement", RequirementViewSet)
router.register("project-case-ref", ProjectCaseRefViewSet)
router.register("project-suite-ref", ProjectSuiteRefViewSet)
router.register("sprint-case-ref", SprintCaseRefViewSet)
router.register("sprint-suite-ref", SprintSuiteRefViewSet)


urlpatterns = router.urls