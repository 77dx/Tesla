from django.urls import path

from .views import EndpointViewSet, CaseViewSet, run_pytest
from rest_framework import routers


urlpatterns = [
    path('run/', run_pytest)
]

router = routers.SimpleRouter()
router.register("endpoint", EndpointViewSet)
router.register("case", CaseViewSet)

urlpatterns += router.urls

