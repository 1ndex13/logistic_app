from django.db import models
from django.conf import settings
from warehouses.models import Warehouse

class Driver(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='driver_profile',
        limit_choices_to={'role': 'DRIVER'},
        verbose_name='Пользователь'
    )
    license_number = models.CharField(max_length=50, unique=True, verbose_name='Номер водительского удостоверения')
    license_category = models.CharField(max_length=10, verbose_name='Категория прав')
    license_expiry = models.DateField(verbose_name='Срок действия прав')
    phone_number = models.CharField(max_length=20, verbose_name='Номер телефона')
    vehicle = models.ForeignKey(
        'Vehicle', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_drivers',
        verbose_name='Закрепленное ТС'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Водитель'
        verbose_name_plural = 'Водители'

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.license_number}"

class Vehicle(models.Model):
    VEHICLE_TYPE_CHOICES = (
        ('TRUCK', 'Грузовик'),
        ('VAN', 'Фургон'),
        ('TRAILER', 'Прицеп'),
        ('SPECIAL', 'Спецтранспорт'),
    )
    
    STATUS_CHOICES = (
        ('AVAILABLE', 'Доступен'),
        ('IN_USE', 'В работе'),
        ('MAINTENANCE', 'На обслуживании'),
        ('BROKEN', 'Сломан'),
    )

    license_plate = models.CharField(max_length=20, unique=True, verbose_name='Госномер')
    model = models.CharField(max_length=100, verbose_name='Модель')
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPE_CHOICES, default='TRUCK', verbose_name='Тип транспорта')
    
    current_warehouse = models.ForeignKey(
        Warehouse, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name='Текущий склад'
    )
    
    capacity = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='Грузоподъемность (т)'
    )
    volume = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='Объем (м³)'
    )
    
    cargo_recipient = models.CharField(
        max_length=200, 
        blank=True, 
        verbose_name='Грузополучатель'
    )
    cargo_description = models.TextField(
        blank=True, 
        verbose_name='Описание груза'
    )
    cargo_volume = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='Объем ТМЦ'
    )
    
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='AVAILABLE', 
        verbose_name='Статус'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Транспортное средство'
        verbose_name_plural = 'Транспортные средства'

    def __str__(self):
        return f"{self.model} - {self.license_plate}"