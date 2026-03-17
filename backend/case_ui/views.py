from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets

from .models import Element, Case
from .serializers import ElementSerializer, CaseUISerializer

@extend_schema(tags=["Case_UI"])
class ElementViewSet(viewsets.ModelViewSet):
    queryset = Element.objects.all().order_by('-id')
    serializer_class = ElementSerializer


@extend_schema(tags=["Case_UI"])
class CaseViewSet(viewsets.ModelViewSet):
    queryset = Case.objects.all().order_by('-id')
    serializer_class = CaseUISerializer
