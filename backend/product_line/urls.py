from rest_framework.routers import DefaultRouter
from .views import ProductLineViewSet

router = DefaultRouter()
router.register('', ProductLineViewSet, basename='product-line')

urlpatterns = router.urls
