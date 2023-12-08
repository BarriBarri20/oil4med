from rest_framework.routers import SimpleRouter

from dbmanage.views import UserViewSet, OliveGroveListRetrieveViewSet, OliveGroveModelViewSet

router = SimpleRouter()

# Register all viewsets here
router.register("users", UserViewSet)
router.register("olive-grove", OliveGroveListRetrieveViewSet, basename='olive-grove')
router.register("olive-grove-objects", OliveGroveModelViewSet, basename='olive-grove-objects')


app_name = "api"
urlpatterns = router.urls
