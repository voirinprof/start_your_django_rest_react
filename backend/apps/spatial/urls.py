from rest_framework.routers import DefaultRouter

from .views import PointOfInterestViewSet, ZoneViewSet

router = DefaultRouter()
router.register(r"points", PointOfInterestViewSet, basename="point-of-interest")
router.register(r"zones", ZoneViewSet, basename="zone")

urlpatterns = router.urls
