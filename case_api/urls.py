from .views import EndpontViewSet, CaseViewSet
from rest_framework import routers


router = routers.SimpleRouter()
router.register("endpoint", EndpontViewSet)
router.register("case", CaseViewSet)


urlpatterns = router.urls