from django.contrib import admin
from .models import Warehouse

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'capacity', 'current_load', 'utilization_percentage', 'contact_person', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'address', 'specialization')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'address', 'is_active')
        }),
        ('Характеристики', {
            'fields': ('capacity', 'current_load', 'specialization', 'working_hours')
        }),
        ('Координаты', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',)
        }),
        ('Контакты', {
            'fields': ('contact_person',)
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def utilization_percentage(self, obj):
        return f"{obj.utilization_percentage()}%"
    utilization_percentage.short_description = 'Загруженность'