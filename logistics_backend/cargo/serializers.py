from rest_framework import serializers
from .models import CargoType, Shipment
from warehouses.serializers import WarehouseSerializer
from vehicles.serializers import VehicleSerializer, DriverSerializer
from core.serializers import UserProfileSerializer


class CargoTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CargoType
        fields = [
            'id', 'name', 'description', 'hazard_class',
            'requires_special_handling', 'max_temperature',
            'min_temperature', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ShipmentSerializer(serializers.ModelSerializer):
    cargo_type_details = CargoTypeSerializer(source='cargo_type', read_only=True)
    origin_warehouse_details = WarehouseSerializer(source='origin_warehouse', read_only=True)
    destination_warehouse_details = WarehouseSerializer(source='destination_warehouse', read_only=True)
    assigned_vehicle_details = VehicleSerializer(source='assigned_vehicle', read_only=True)
    assigned_driver_details = DriverSerializer(source='assigned_driver', read_only=True)
    created_by_details = UserProfileSerializer(source='created_by', read_only=True)
    assigned_by_details = UserProfileSerializer(source='assigned_by', read_only=True)
    duration = serializers.SerializerMethodField()
    is_delayed = serializers.SerializerMethodField()

    class Meta:
        model = Shipment
        fields = [
            'id', 'cargo_type', 'cargo_type_details', 'weight', 'volume', 'description',
            'origin_warehouse', 'origin_warehouse_details', 'destination_warehouse', 'destination_warehouse_details',
            'planned_departure', 'planned_arrival', 'actual_departure', 'actual_arrival',
            'assigned_vehicle', 'assigned_vehicle_details', 'assigned_driver', 'assigned_driver_details',
            'status', 'priority', 'created_by', 'created_by_details', 'assigned_by', 'assigned_by_details',
            'special_instructions', 'delay_reason', 'duration', 'is_delayed',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_duration(self, obj):
        duration = obj.calculate_duration()
        if duration:
            return str(duration)
        return None

    def get_is_delayed(self, obj):
        return obj.is_delayed()

    def validate(self, data):
        if data.get('planned_arrival') and data.get('planned_departure'):
            if data['planned_arrival'] <= data['planned_departure']:
                raise serializers.ValidationError({
                    'planned_arrival': 'Время прибытия должно быть позже времени отправления'
                })

        if data.get('origin_warehouse') and data.get('destination_warehouse'):
            if data['origin_warehouse'] == data['destination_warehouse']:
                raise serializers.ValidationError({
                    'destination_warehouse': 'Склад назначения не может совпадать со складом отправления'
                })

        return data


class AssignShipmentSerializer(serializers.Serializer):
    vehicle_id = serializers.IntegerField()
    driver_id = serializers.IntegerField()

    def validate(self, attrs):
        from vehicles.models import Vehicle, Driver

        try:
            vehicle = Vehicle.objects.get(id=attrs['vehicle_id'])
            driver = Driver.objects.get(id=attrs['driver_id'])
        except (Vehicle.DoesNotExist, Driver.DoesNotExist):
            raise serializers.ValidationError("Транспорт или водитель не найдены")

        if driver.vehicle != vehicle:
            raise serializers.ValidationError("Водитель не привязан к указанному транспортному средству")

        attrs['vehicle'] = vehicle
        attrs['driver'] = driver
        return attrs


class UpdateShipmentStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Shipment.STATUS_CHOICES)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_status(self, value):
        return value