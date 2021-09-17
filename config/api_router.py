from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from fires_watch.fires.api.views import FiresViewSet
from fires_watch.users.api.views import UserViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register("fires", FiresViewSet, basename="fires")

app_name = "api"
urlpatterns = router.urls
