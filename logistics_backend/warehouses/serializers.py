from rest_framework import serializers
from .models import Warehouse
from core.serializers import UserProfileSerializer

class WarehouseSerializer(serializers.ModelSerializer):
    contact_person_details = UserProfileSerializer(source='contact_person', read_only=True)
    utilization_percentage = serializers.ReadOnlyField()

    class Meta:
        model = Warehouse
        fields = [
            'id', 'name', 'address', 'capacity', 'current_load',
            'specialization', 'working_hours', 'contact_person',
            'contact_person_details', 'latitude', 'longitude',
            'is_active', 'utilization_percentage', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_capacity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Вместимость должна быть положительным числом.")
        return value

    def validate_contact_person(self, value):
        if value and value.role not in ['LOGISTICS_MANAGER', 'DISPATCHER']:
            raise serializers.ValidationError(
                "Ответственным лицом может быть только Логист или Диспетчер"
            )
        return value