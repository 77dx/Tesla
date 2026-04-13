from rest_framework.routers import DefaultRouter

from .views import AutomationProjectViewSet, AutomationSuiteViewSet, AutomationRunViewSet

router = DefaultRouter()
router.register('project', AutomationProjectViewSet)
router.register('suite', AutomationSuiteViewSet)
router.register('run', AutomationRunViewSet)

urlpatterns = router.urls
