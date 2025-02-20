from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from .models import Project, Config
from .serializers import ProjectSerializer, ConfigSerializer


@extend_schema(tags=["Project"])
class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


@extend_schema(tags=["Project"])
class ConfigViewSet(viewsets.ModelViewSet):
    queryset = Config.objects.all()
    serializer_class = ConfigSerializer


