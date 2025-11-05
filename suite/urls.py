from django.urls import path
from .views import SuiteViewSet, RunResultViewSet, static_server
from rest_framework import routers


router = routers.SimpleRouter()
router.register("suite", SuiteViewSet)
router.register("result", RunResultViewSet)

urlpatterns = [
    path("static/<path:path>", static_server, {"document_root": "upload_yaml"})
]

urlpatterns += router.urls

