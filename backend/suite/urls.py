from django.urls import path
from .views import SuiteViewSet, SuiteCaseItemViewSet, RunResultViewSet, static_server, EnvironmentViewSet, GlobalVariableViewSet, ServiceViewSet
from rest_framework import routers

router = routers.SimpleRouter()
router.register("suite", SuiteViewSet)
router.register("suite-case-item", SuiteCaseItemViewSet)
router.register("runresult", RunResultViewSet)
router.register("environment", EnvironmentViewSet)
router.register("global-variable", GlobalVariableViewSet)
router.register("service", ServiceViewSet)

urlpatterns = [
    path("static/<path:path>", static_server, {"document_root": "upload_yaml"})
]

urlpatterns += router.urls
