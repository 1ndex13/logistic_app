from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CargoTypeViewSet, ShipmentViewSet

router = DefaultRouter()
router.register(r'cargo-types', CargoTypeViewSet, basename='cargo-types')
router.register(r'shipments', ShipmentViewSet, basename='shipments')

urlpatterns = [
    path('', include(router.urls)),
]