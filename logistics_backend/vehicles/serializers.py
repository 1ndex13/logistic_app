from rest_framework import serializers
from .models import Vehicle, Driver
from core.serializers import UserProfileSerializer


class VehicleSerializer(serializers.ModelSerializer):
    current_driver_details = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = [
            'id', 'license_plate', 'model', 'vehicle_type', 'capacity',
            'volume', 'status', 'current_driver', 'current_driver_details',
            'year', 'vin', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_current_driver_details(self, obj):
        if obj.current_driver:
            return DriverSerializer(obj.current_driver).data
        return None

    def validate_capacity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Грузоподъемность должна быть положительным числом.")
        return value

    def validate_volume(self, value):
        if value <= 0:
            raise serializers.ValidationError("Объем должен быть положительным числом.")
        return value


class DriverSerializer(serializers.ModelSerializer):
    user_details = UserProfileSerializer(source='user', read_only=True)
    vehicle_details = VehicleSerializer(source='vehicle', read_only=True)

    class Meta:
        model = Driver
        fields = [
            'id', 'user', 'user_details', 'license_number', 'license_category',
            'license_expiry', 'phone_number', 'vehicle', 'vehicle_details',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_user(self, value):
        if value.role != 'DRIVER':
            raise serializers.ValidationError("Пользователь должен иметь роль Водитель")
        return value


class AssignVehicleSerializer(serializers.Serializer):
    vehicle_id = serializers.IntegerField()
    driver_id = serializers.IntegerField()

    def validate(self, attrs):
        try:
            vehicle = Vehicle.objects.get(id=attrs['vehicle_id'])
            driver = Driver.objects.get(id=attrs['driver_id'])
        except (Vehicle.DoesNotExist, Driver.DoesNotExist):
            raise serializers.ValidationError("Транспорт или водитель не найдены")

        attrs['vehicle'] = vehicle
        attrs['driver'] = driver
        return attrs