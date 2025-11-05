from django.contrib import admin
from .models import CargoType, Shipment

@admin.register(CargoType)
class CargoTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'hazard_class', 'requires_special_handling', 'is_active')
    list_filter = ('hazard_class', 'requires_special_handling', 'is_active')
    search_fields = ('name', 'description')

@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'cargo_type', 'status', 'priority', 'origin_warehouse', 'destination_warehouse', 'planned_departure')
    list_filter = ('status', 'priority', 'created_at')
    search_fields = ('cargo_type__name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('assigned_vehicle', 'assigned_driver')