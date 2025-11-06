from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Vehicle, Driver
from .serializers import VehicleSerializer, DriverSerializer, AssignVehicleSerializer


class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Vehicle.objects.all()


        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

 
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')


        vehicle_type = self.request.query_params.get('type', None)
        if vehicle_type:
            queryset = queryset.filter(vehicle_type=vehicle_type)

 
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(license_plate__icontains=search) |
                Q(model__icontains=search)
            )

        return queryset

    @action(detail=False, methods=['get'])
    def stats(self, request):
        total_vehicles = Vehicle.objects.count()
        available_vehicles = Vehicle.objects.filter(status='AVAILABLE').count()
        in_use_vehicles = Vehicle.objects.filter(status='IN_USE').count()
        maintenance_vehicles = Vehicle.objects.filter(status='MAINTENANCE').count()

        return Response({
            'total_vehicles': total_vehicles,
            'available_vehicles': available_vehicles,
            'in_use_vehicles': in_use_vehicles,
            'maintenance_vehicles': maintenance_vehicles,
            'utilization_rate': round((in_use_vehicles / total_vehicles * 100) if total_vehicles > 0 else 0, 2)
        })

    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        vehicle = self.get_object()
        new_status = request.data.get('status')

        if new_status not in dict(Vehicle.STATUS_CHOICES):
            return Response(
                {'error': 'Неверный статус'},
                status=status.HTTP_400_BAD_REQUEST
            )

        vehicle.status = new_status
        vehicle.save()

        serializer = self.get_serializer(vehicle)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def update_warehouse(self, request, pk=None):
        vehicle = self.get_object()
        warehouse_id = request.data.get('current_warehouse')
        
        if warehouse_id:
            try:
                from warehouses.models import Warehouse
                warehouse = Warehouse.objects.get(id=warehouse_id)
                vehicle.current_warehouse = warehouse
                vehicle.save()
            except Warehouse.DoesNotExist:
                return Response(
                    {'error': 'Склад не найден'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            vehicle.current_warehouse = None
            vehicle.save()
            
        serializer = self.get_serializer(vehicle)
        return Response(serializer.data)

class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Driver.objects.all()

        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        has_vehicle = self.request.query_params.get('has_vehicle', None)
        if has_vehicle is not None:
            if has_vehicle.lower() == 'true':
                queryset = queryset.filter(vehicle__isnull=False)
            else:
                queryset = queryset.filter(vehicle__isnull=True)

        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(license_number__icontains=search)
            )

        return queryset

    @action(detail=False, methods=['get'])
    def available(self, request):
        """Список водителей без закрепленного ТС"""
        available_drivers = Driver.objects.filter(vehicle__isnull=True, is_active=True)
        serializer = self.get_serializer(available_drivers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def assign_vehicle(self, request):
        serializer = AssignVehicleSerializer(data=request.data)
        if serializer.is_valid():
            vehicle = serializer.validated_data['vehicle']
            driver = serializer.validated_data['driver']

            if driver.vehicle:
                old_vehicle = driver.vehicle
                old_vehicle.current_driver = None
                old_vehicle.save()

            driver.vehicle = vehicle
            driver.save()

            vehicle.current_driver = driver
            vehicle.status = 'AVAILABLE'
            vehicle.save()

            return Response({
                'message': 'Транспорт успешно назначен водителю',
                'vehicle': VehicleSerializer(vehicle).data,
                'driver': DriverSerializer(driver).data
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def unassign_vehicle(self, request, pk=None):
        driver = self.get_object()

        if driver.vehicle:
            vehicle = driver.vehicle
            vehicle.current_driver = None
            vehicle.save()

            driver.vehicle = None
            driver.save()

            return Response({
                'message': 'Транспорт успешно откреплен от водителя'
            })

        return Response(
            {'error': 'У водителя нет закрепленного транспорта'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['post'])
    def bulk_allocate(self, request):

        vehicle_ids = request.data.get('vehicle_ids', [])
        warehouse_id = request.data.get('warehouse_id')
    

        vehicles = Vehicle.objects.filter(id__in=vehicle_ids, status='AVAILABLE')
        warehouse = Warehouse.objects.get(id=warehouse_id)
    
        for vehicle in vehicles:
            vehicle.status = 'IN_USE'
            vehicle.current_warehouse = warehouse
            vehicle.save()
    
        return Response({'message': f'{vehicles.count()} машин распределено на склад'})

    @action(detail=False, methods=['get'])
    def waiting_allocation(self, request):

        vehicles = Vehicle.objects.filter(
            Q(status='AVAILABLE') | Q(status='WAITING_ALLOCATION')
    )
        serializer = self.get_serializer(vehicles, many=True)
        return Response(serializer.data)