from django.urls import path
from .views import (
    SuiteViewSet, SuiteNodeViewSet, SuiteCaseItemViewSet, RunResultViewSet, SuiteExecutionLogViewSet, static_server,
    EnvironmentViewSet, GlobalVariableViewSet, ServiceViewSet, DataSetViewSet,
    ExecutionSnapshotViewSet, ImportJobViewSet,
)
from .performance_views import PerformanceTestViewSet
from .perf_views import PerformanceConfigViewSet, PerformanceResultViewSet
from rest_framework import routers

router = routers.SimpleRouter()
router.register("suite", SuiteViewSet)
router.register("suite-node", SuiteNodeViewSet, basename='suite-node')
router.register("suite-case-item", SuiteCaseItemViewSet)
router.register("runresult", RunResultViewSet)
router.register("suite-execution-log", SuiteExecutionLogViewSet)
router.register("environment", EnvironmentViewSet)
router.register("global-variable", GlobalVariableViewSet)
router.register("service", ServiceViewSet)
router.register("performance", PerformanceTestViewSet)  # 旧接口保留兼容
router.register("perf-config", PerformanceConfigViewSet)
router.register("perf-result", PerformanceResultViewSet)
router.register("dataset", DataSetViewSet)
router.register("execution-snapshot", ExecutionSnapshotViewSet)
router.register("import-job", ImportJobViewSet)

urlpatterns = [
    path("static/<path:path>", static_server, {"document_root": "upload_yaml"})
]

urlpatterns += router.urls
