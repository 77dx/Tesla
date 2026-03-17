from django.urls import path

from .views import EndpointViewSet, CaseViewSet, run_pytest, run_case
from rest_framework import routers


urlpatterns = [
    path('run/', run_pytest),
    path('run_case/', run_case),
]

router = routers.SimpleRouter()
router.register("endpoint", EndpointViewSet)
router.register("case", CaseViewSet)

urlpatterns += router.urls

