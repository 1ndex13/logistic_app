import pandas as pd
import re
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction, models
from .models import Vehicle, Driver
from .serializers import (
    VehicleSerializer, DriverSerializer, VehicleImportSerializer, AssignVehicleSerializer
)
from warehouses.models import Warehouse

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Vehicle.objects.all()
        
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        warehouse_filter = self.request.query_params.get('warehouse', None)
        if warehouse_filter:
            queryset = queryset.filter(current_warehouse_id=warehouse_filter)
            
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                models.Q(license_plate__icontains=search) |
                models.Q(model__icontains=search) |
                models.Q(cargo_recipient__icontains=search)
            )
            
        return queryset

    def parse_volume(self, volume_str):
        if pd.isna(volume_str) or volume_str == '':
            return None
        
        try:
            str_value = str(volume_str).strip().replace(',', '.')
            str_value = re.sub(r'[^\d.-]', '', str_value)
            return float(str_value) if str_value else None
        except (ValueError, TypeError):
            return None

    def extract_warehouse_number(self, warehouse_info):
        if pd.isna(warehouse_info) or not warehouse_info:
            return None
        
        warehouse_str = str(warehouse_info)
        patterns = [
            r'№\s*(\d+)',
            r'склад\s*№\s*(\d+)',
            r'база\s*скл\.?\s*№\s*(\d+)',
            r'(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, warehouse_str, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None

    def get_or_create_warehouse(self, warehouse_number):
        """Находит или создает склад по номеру"""
        if not warehouse_number:
            return None
        
        try:
            warehouse = Warehouse.objects.filter(
                models.Q(name__icontains=warehouse_number) |
                models.Q(address__icontains=warehouse_number)
            ).first()
            
            if not warehouse:
                warehouse = Warehouse.objects.create(
                    name=f'Склад {warehouse_number}',
                    address=f'Адрес склада {warehouse_number}',
                    capacity=1000,
                    current_load=0,
                    is_active=True
                )
            
            return warehouse
        except Exception:
            return None

    @action(detail=False, methods=['post'], url_path='upload-excel')
    def upload_excel(self, request):
        serializer = VehicleImportSerializer(data=request.data)
        
        if serializer.is_valid():
            excel_file = serializer.validated_data['file']
            
            try:
                df = pd.read_excel(excel_file, sheet_name='14.09.2023')

                data_df = df.iloc[4:].reset_index(drop=True)
                
                vehicles_created = 0
                errors = []
                processed_license_plates = set()

                vehicle_data_list = []
                
                for index, row in data_df.iterrows():
                    try:

                        if pd.isna(row.iloc[3]) or pd.isna(row.iloc[4]):
                            continue

                        cargo_recipient = str(row.iloc[1]) if not pd.isna(row.iloc[1]) else ""
                        vehicle_model = str(row.iloc[3])
                        license_plate = str(row.iloc[4]).strip()
                        warehouse_info = str(row.iloc[5]) if not pd.isna(row.iloc[5]) else ""
                        cargo_description = str(row.iloc[23]) if not pd.isna(row.iloc[23]) else ""
                        cargo_volume = self.parse_volume(row.iloc[22])

                        if license_plate in processed_license_plates:
                            errors.append(f"Строка {index + 5}: дубликат госномера {license_plate}")
                            continue
                        
                        processed_license_plates.add(license_plate)
                        
                        vehicle_data_list.append({
                            'cargo_recipient': cargo_recipient,
                            'vehicle_model': vehicle_model,
                            'license_plate': license_plate,
                            'warehouse_info': warehouse_info,
                            'cargo_description': cargo_description,
                            'cargo_volume': cargo_volume,
                            'row_index': index + 5
                        })
                        
                    except Exception as e:
                        errors.append(f"Строка {index + 5}: ошибка чтения данных - {str(e)}")
                        continue

                with transaction.atomic():
                    Vehicle.objects.all().delete()
                    
                    for vehicle_data in vehicle_data_list:
                        try:
                            license_plate = vehicle_data['license_plate']

                            if Vehicle.objects.filter(license_plate=license_plate).exists():
                                errors.append(f"Строка {vehicle_data['row_index']}: госномер {license_plate} уже существует в БД")
                                continue

                            warehouse_number = self.extract_warehouse_number(vehicle_data['warehouse_info'])
                            warehouse = self.get_or_create_warehouse(warehouse_number)

                            Vehicle.objects.create(
                                license_plate=license_plate,
                                model=vehicle_data['vehicle_model'],
                                vehicle_type='TRUCK',
                                current_warehouse=warehouse,
                                cargo_recipient=vehicle_data['cargo_recipient'],
                                cargo_description=vehicle_data['cargo_description'],
                                cargo_volume=vehicle_data['cargo_volume'],
                                status='AVAILABLE'
                            )
                            
                            vehicles_created += 1
                            
                        except Exception as e:
                            errors.append(f"Строка {vehicle_data['row_index']}: ошибка создания - {str(e)}")
                            continue
                
                response_data = {
                    'message': f'Успешно создано {vehicles_created} записей',
                    'vehicles_created': vehicles_created
                }
                
                if errors:
                    response_data['errors'] = errors[:10]
                
                return Response(response_data, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response(
                    {'error': f'Ошибка обработки файла: {str(e)}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        total_vehicles = Vehicle.objects.count()
        available_vehicles = Vehicle.objects.filter(status='AVAILABLE').count()
        in_use_vehicles = Vehicle.objects.filter(status='IN_USE').count()
        
        return Response({
            'total_vehicles': total_vehicles,
            'available_vehicles': available_vehicles,
            'in_use_vehicles': in_use_vehicles,
        })

    @action(detail=True, methods=['post'])
    def assign_driver(self, request, pk=None):
        vehicle = self.get_object()
        serializer = AssignVehicleSerializer(data=request.data)
        
        if serializer.is_valid():
            driver = serializer.validated_data['driver']

            vehicle.driver = driver
            vehicle.status = 'IN_USE'
            vehicle.save()

            driver.vehicle = vehicle
            driver.save()
            
            return Response(VehicleSerializer(vehicle).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Driver.objects.all()
        
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        vehicle_filter = self.request.query_params.get('vehicle', None)
        if vehicle_filter:
            queryset = queryset.filter(vehicle_id=vehicle_filter)
            
        return queryset.select_related('user', 'vehicle')

    @action(detail=False, methods=['get'])
    def available(self, request):
        available_drivers = Driver.objects.filter(
            vehicle__isnull=True,
            is_active=True
        ).select_related('user')
        
        serializer = self.get_serializer(available_drivers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def assign_vehicle(self, request, pk=None):
        driver = self.get_object()
        serializer = AssignVehicleSerializer(data=request.data)
        
        if serializer.is_valid():
            vehicle = serializer.validated_data['vehicle']

            if vehicle.status != 'AVAILABLE':
                return Response(
                    {'error': 'Транспортное средство недоступно'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            driver.vehicle = vehicle
            driver.save()
            
            vehicle.status = 'IN_USE'
            vehicle.save()
            
            return Response(DriverSerializer(driver).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)