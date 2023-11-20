from django.conf import settings
from django.urls import include, path
from rest_framework_nested import routers

from dhanriti.views.tanks import CanvasViewSet, FunnelViewSet, TankViewSet

from .views.auth import APICheckLoginView, APILoginView, APILogoutView
from .views.users import UserViewSet

app_name = "api"

router = routers.SimpleRouter(trailing_slash=False)
NestedRouter = routers.NestedSimpleRouter
if settings.DEBUG:
    router = routers.DefaultRouter(trailing_slash=False)
    NestedRouter = routers.NestedDefaultRouter

router.register(r"users", UserViewSet)
router.register(r"canvases", CanvasViewSet)

canvas_router = NestedRouter(router, r"canvases", lookup="canvas")
canvas_router.register(r"tanks", TankViewSet, basename="canvas-tanks")
canvas_router.register(r"funnels", FunnelViewSet, basename="canvas-funnels")

auth_urls = [
    path("login", APILoginView.as_view(), name="login"),
    path("logout", APILogoutView.as_view(), name="logout"),
]
router.register(r"auth/check", APICheckLoginView, basename="check")

urlpatterns = [
    path(r"", include(router.urls)),
    path("auth/", include(auth_urls)),
    path(r"", include(canvas_router.urls)),
]
