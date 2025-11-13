from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)
from .views import UserViewSet, CustomTokenObtainPairView


# Create router and register viewsets
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

app_name = 'user'

urlpatterns = [
    # User authentication endpoints
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # User API endpoints (from router)
    path('', include(router.urls)),
]
