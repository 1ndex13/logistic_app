from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Warehouse
from .serializers import WarehouseSerializer


class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Warehouse.objects.all()


        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        contact_person = self.request.query_params.get('contact_person', None)
        if contact_person:
            queryset = queryset.filter(contact_person_id=contact_person)

        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(address__icontains=search)
            )

        return queryset

    @action(detail=False, methods=['get'])
    def available_managers(self, request):
        """Список доступных логистов и диспетчеров для назначения"""
        from core.models import User
        managers = User.objects.filter(role__in=['LOGISTICS_MANAGER', 'DISPATCHER'])
        from core.serializers import UserProfileSerializer
        serializer = UserProfileSerializer(managers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        total_warehouses = Warehouse.objects.count()
        active_warehouses = Warehouse.objects.filter(is_active=True).count()
        total_capacity = sum(warehouse.capacity for warehouse in Warehouse.objects.all())
        avg_utilization = sum(warehouse.utilization_percentage() for warehouse in
                              Warehouse.objects.all()) / total_warehouses if total_warehouses > 0 else 0

        return Response({
            'total_warehouses': total_warehouses,
            'active_warehouses': active_warehouses,
            'total_capacity': total_capacity,
            'average_utilization': round(avg_utilization, 2)
        })

    @action(detail=True, methods=['post'])
    def update_load(self, request, pk=None):
        warehouse = self.get_object()
        new_load = request.data.get('current_load')

        if new_load is None:
            return Response(
                {'error': 'Параметр current_load обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            new_load = float(new_load)
            if new_load < 0 or new_load > warehouse.capacity:
                return Response(
                    {'error': f'Загрузка должна быть между 0 и {warehouse.capacity}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            warehouse.current_load = new_load
            warehouse.save()

            serializer = self.get_serializer(warehouse)
            return Response(serializer.data)

        except ValueError:
            return Response(
                {'error': 'Некорректное значение загрузки'},
                status=status.HTTP_400_BAD_REQUEST
            )