from rest_framework.routers import DefaultRouter

from .views import ResponderProfileViewSet

router = DefaultRouter()
router.register('', ResponderProfileViewSet, basename='responder')

urlpatterns = router.urls
