# vehicles/models.py
from django.db import models
from django.core.exceptions import ValidationError
from core.models import User


class Vehicle(models.Model):
    VEHICLE_TYPES = (
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
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES, verbose_name='Тип транспорта')
    capacity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Грузоподъемность (т)')
    volume = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Объем (м³)')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE', verbose_name='Статус')
    
    # ДОБАВЛЯЕМ ПОЛЕ current_warehouse ВНУТРИ КЛАССА Vehicle
    current_warehouse = models.ForeignKey(
        'warehouses.Warehouse',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Текущий склад'
    )
    
    current_driver = models.ForeignKey(
        'Driver',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Текущий водитель',
        related_name='current_vehicle'
    )
    year = models.PositiveIntegerField(verbose_name='Год выпуска')
    vin = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name='VIN')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Транспортное средство'
        verbose_name_plural = 'Транспортные средства'

    def __str__(self):
        return f"{self.model} ({self.license_plate})"

    def clean(self):
        if self.current_driver and self.current_driver.vehicle != self:
            raise ValidationError({
                'current_driver': 'Этот водитель не привязан к данному транспортному средству'
            })


class Driver(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='driver_profile',
        limit_choices_to={'role': 'DRIVER'}
    )
    license_number = models.CharField(max_length=50, unique=True, verbose_name='Номер водительского удостоверения')
    license_category = models.CharField(max_length=10, verbose_name='Категория прав')
    license_expiry = models.DateField(verbose_name='Срок действия прав')
    phone_number = models.CharField(max_length=20, verbose_name='Номер телефона')
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Закрепленное ТС',
        related_name='assigned_drivers'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Водитель'
        verbose_name_plural = 'Водители'

    def clean(self):
        if self.user.role != 'DRIVER':
            raise ValidationError({
                'user': 'Пользователь должен иметь роль Водитель'
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.license_number})"