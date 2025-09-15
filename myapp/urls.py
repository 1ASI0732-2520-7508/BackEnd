from django.urls import path, include
from rest_framework.routers import DefaultRouter
from myapp.views import LogEntryViewSet
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    UserViewSet, CompanyViewSet, SupplierViewSet,
    CategoryViewSet, ItemViewSet, MyTokenObtainPairView,
    CurrentUserView, GroupViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'companies', CompanyViewSet)
router.register(r'suppliers', SupplierViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'items', ItemViewSet)
router.register(r'groups', GroupViewSet) # Endpoint for managing roles/groups
router.register(r'logs', LogEntryViewSet, basename="logs")

urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/', CurrentUserView.as_view(), name='current_user'), # Endpoint to get current user's data
]