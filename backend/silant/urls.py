from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .api_views import (
    MachineViewSet, MaintenanceViewSet, ComplaintViewSet, ReferenceViewSet,
    PublicMachineBySerial
)

router = DefaultRouter()
router.register(r"machines", MachineViewSet)
router.register(r"maintenance", MaintenanceViewSet)
router.register(r"complaints", ComplaintViewSet)
router.register(r"references", ReferenceViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
    path("api/public/machine-by-serial/", PublicMachineBySerial.as_view()),
    path("api/auth/jwt/create/", TokenObtainPairView.as_view(), name="jwt_obtain"),
    path("api/auth/jwt/refresh/", TokenRefreshView.as_view(), name="jwt_refresh"),
]
