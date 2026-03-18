from drf_spectacular.utils import extend_schema
from .models import Project, Config
from .serializers import ProjectSerializer, ConfigSerializer
from snippet.base_viewset import BaseViewSet


@extend_schema(tags=["Project"])
class ProjectViewSet(BaseViewSet):
    queryset = Project.objects.all().order_by('-id')
    serializer_class = ProjectSerializer
    search_fields = ['name', 'id']
    product_line_field = 'product_line_id'


@extend_schema(tags=["Project"])
class ConfigViewSet(BaseViewSet):
    queryset = Config.objects.all().order_by('-id')
    serializer_class = ConfigSerializer
    product_line_field = None


