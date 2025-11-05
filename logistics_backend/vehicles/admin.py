from django.contrib import admin
from .models import Vehicle, Driver

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('license_plate', 'model', 'vehicle_type', 'status', 'current_driver', 'is_active')
    list_filter = ('status', 'vehicle_type', 'is_active', 'created_at')
    search_fields = ('license_plate', 'model', 'vin')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'license_number', 'license_category', 'vehicle', 'is_active')
    list_filter = ('is_active', 'license_category', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'license_number')
    readonly_fields = ('created_at', 'updated_at')

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'ФИО'