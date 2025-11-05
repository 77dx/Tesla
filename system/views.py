from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from Tesla.customPagination import CustomPageNumberPagination
from .models import Department, Position, Role
from .serializers import DepartmentSerializer, DepartmentListSerializer, PositionSerializer, RoleSerializer


@extend_schema(tags=["System"])
class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all().order_by('-id')
    serializer_class = DepartmentSerializer
    pagination_class = CustomPageNumberPagination

    def get_serializer_class(self):
        if self.action == "list":
            return DepartmentListSerializer
        return super().get_serializer_class()

@extend_schema(tags=["System"])
class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer


@extend_schema(tags=["System"])
class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer