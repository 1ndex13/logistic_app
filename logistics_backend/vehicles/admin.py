from django.contrib import admin
from .models import Vehicle, Driver

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('user', 'license_number', 'license_category', 'phone_number', 'vehicle', 'is_active')
    list_filter = ('is_active', 'license_category')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'license_number')
    raw_id_fields = ('user', 'vehicle')

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('license_plate', 'model', 'vehicle_type', 'status', 'current_warehouse', 'is_active')
    list_filter = ('status', 'vehicle_type', 'is_active', 'current_warehouse')
    search_fields = ('license_plate', 'model', 'cargo_recipient')
    raw_id_fields = ('current_warehouse',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('current_warehouse')