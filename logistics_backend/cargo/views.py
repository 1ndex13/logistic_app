from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta
from .models import CargoType, Shipment
from .serializers import (
    CargoTypeSerializer, ShipmentSerializer,
    AssignShipmentSerializer, UpdateShipmentStatusSerializer
)


class CargoTypeViewSet(viewsets.ModelViewSet):
    queryset = CargoType.objects.all()
    serializer_class = CargoTypeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = CargoType.objects.all()

        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(name__icontains=search)

        return queryset


class ShipmentViewSet(viewsets.ModelViewSet):
    queryset = Shipment.objects.all()
    serializer_class = ShipmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Shipment.objects.all()
        user = self.request.user

        if user.role == 'DRIVER' and hasattr(user, 'driver_profile'):
            queryset = queryset.filter(assigned_driver=user.driver_profile)
            
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        priority_filter = self.request.query_params.get('priority', None)
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)

        warehouse_filter = self.request.query_params.get('warehouse', None)
        if warehouse_filter:
            queryset = queryset.filter(
                Q(origin_warehouse_id=warehouse_filter) |
                Q(destination_warehouse_id=warehouse_filter)
            )

        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        if date_from:
            queryset = queryset.filter(planned_departure__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(planned_departure__date__lte=date_to)


        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(cargo_type__name__icontains=search) |
                Q(description__icontains=search)
            )

        return queryset.select_related(
            'cargo_type', 'origin_warehouse', 'destination_warehouse',
            'assigned_vehicle', 'assigned_driver', 'created_by', 'assigned_by'
        )

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        shipment = self.get_object()
        serializer = AssignShipmentSerializer(data=request.data)

        if serializer.is_valid():
            vehicle = serializer.validated_data['vehicle']
            driver = serializer.validated_data['driver']

            if vehicle.status != 'AVAILABLE':
                return Response(
                    {'error': 'Транспортное средство недоступно'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            shipment.assigned_vehicle = vehicle
            shipment.assigned_driver = driver
            shipment.assigned_by = request.user
            shipment.status = 'ASSIGNED'
            shipment.save()

            vehicle.status = 'IN_USE'
            vehicle.save()

            return Response(ShipmentSerializer(shipment).data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        shipment = self.get_object()
        serializer = UpdateShipmentStatusSerializer(data=request.data)

        if serializer.is_valid():
            new_status = serializer.validated_data['status']
            notes = serializer.validated_data.get('notes', '')

            if new_status == 'IN_TRANSIT' and not shipment.actual_departure:
                shipment.actual_departure = timezone.now()
            elif new_status == 'COMPLETED' and not shipment.actual_arrival:
                shipment.actual_arrival = timezone.now()
            elif new_status == 'DELAYED':
                shipment.delay_reason = notes

            shipment.status = new_status
            shipment.save()

            return Response(ShipmentSerializer(shipment).data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        status_stats = Shipment.objects.values('status').annotate(
            count=Count('id')
        )

        priority_stats = Shipment.objects.values('priority').annotate(
            count=Count('id')
        )
        completed_shipments = Shipment.objects.filter(
            status='COMPLETED',
            actual_departure__isnull=False,
            actual_arrival__isnull=False
        )

        avg_delivery_time = None
        if completed_shipments.exists():
            total_seconds = sum(
                (ship.actual_arrival - ship.actual_departure).total_seconds()
                for ship in completed_shipments
            )
            avg_delivery_time = total_seconds / completed_shipments.count()

        return Response({
            'status_stats': list(status_stats),
            'priority_stats': list(priority_stats),
            'total_shipments': Shipment.objects.count(),
            'active_shipments': Shipment.objects.exclude(
                status__in=['COMPLETED', 'CANCELLED']
            ).count(),
            'avg_delivery_time_seconds': avg_delivery_time,
        })

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Предстоящие поставки (на сегодня и завтра)"""
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)

        upcoming_shipments = Shipment.objects.filter(
            planned_departure__date__in=[today, tomorrow],
            status__in=['PLANNED', 'ASSIGNED']
        ).order_by('planned_departure')

        serializer = self.get_serializer(upcoming_shipments, many=True)
        return Response(serializer.data)