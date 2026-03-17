from .views import ElementViewSet, CaseViewSet
from rest_framework import routers


router = routers.SimpleRouter()
router.register("element", ElementViewSet)
router.register("case", CaseViewSet)

urlpatterns = router.urls

