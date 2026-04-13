from django.urls import path

from .views import EndpointViewSet, CaseViewSet, CaseNodeViewSet, run_pytest, run_case
from rest_framework import routers


urlpatterns = [
    path('run/', run_pytest),
    path('run_case/', run_case),
]

router = routers.SimpleRouter()
router.register("endpoint", EndpointViewSet)
router.register("case", CaseViewSet)
router.register("case-node", CaseNodeViewSet, basename='case-node')

urlpatterns += router.urls

