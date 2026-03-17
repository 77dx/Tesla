from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from .models import Project, Config
from .serializers import ProjectSerializer, ConfigSerializer


@extend_schema(tags=["Project"])
class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by('-id')
    serializer_class = ProjectSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get('search')
        if search:
            if search.isdigit():
                qs = qs.filter(id=int(search))
            else:
                qs = qs.filter(name__icontains=search)
        product_line_id = self.request.query_params.get('product_line')
        if product_line_id:
            qs = qs.filter(product_line_id=product_line_id)
        return qs


@extend_schema(tags=["Project"])
class ConfigViewSet(viewsets.ModelViewSet):
    queryset = Config.objects.all().order_by('-id')
    serializer_class = ConfigSerializer


