from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from .models import Endpoint, Case
from .serializers import EndpointSerializer, CaseSerializer


@extend_schema(tags=["Case_API"])
class EndpontViewSet(viewsets.ModelViewSet):
    queryset = Endpoint.objects.all()
    serializer_class = EndpointSerializer


@extend_schema(tags=["Case_API"])
class CaseViewSet(viewsets.ModelViewSet):
    queryset = Case.objects.all()
    serializer_class = CaseSerializer

    def run_pytest(self):
        obj: Case = self.get_object()

