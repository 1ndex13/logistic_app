from django.db import models
from django.core.exceptions import ValidationError
from core.models import User
from warehouses.models import Warehouse
from vehicles.models import Vehicle, Driver


class CargoType(models.Model):
    HAZARD_CLASS_CHOICES = (
        (1, '1 - Взрывчатые вещества'),
        (2, '2 - Газы'),
        (3, '3 - Легковоспламеняющиеся жидкости'),
        (4, '4 - Легковоспламеняющиеся твердые вещества'),
        (5, '5 - Окисляющие вещества'),
        (6, '6 - Токсичные вещества'),
        (7, '7 - Радиоактивные материалы'),
        (8, '8 - Коррозионные вещества'),
        (9, '9 - Прочие опасные вещества'),
    )

    name = models.CharField(max_length=200, verbose_name='Название типа груза')
    description = models.TextField(blank=True, verbose_name='Описание')
    hazard_class = models.PositiveSmallIntegerField(
        choices=HAZARD_CLASS_CHOICES,
        null=True,
        blank=True,
        verbose_name='Класс опасности'
    )
    requires_special_handling = models.BooleanField(default=False, verbose_name='Требует особого обращения')
    max_temperature = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Макс. температура хранения'
    )
    min_temperature = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Мин. температура хранения'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Тип груза'
        verbose_name_plural = 'Типы грузов'

    def __str__(self):
        return self.name

    def clean(self):
        if self.max_temperature and self.min_temperature and self.max_temperature < self.min_temperature:
            raise ValidationError({
                'max_temperature': 'Максимальная температура не может быть меньше минимальной'
            })


class Shipment(models.Model):
    STATUS_CHOICES = (
        ('PLANNED', 'Запланирована'),
        ('ASSIGNED', 'Назначена'),
        ('IN_TRANSIT', 'В пути'),
        ('AT_WAREHOUSE', 'На складе'),
        ('UNLOADING', 'Разгрузка'),
        ('COMPLETED', 'Завершена'),
        ('CANCELLED', 'Отменена'),
        ('DELAYED', 'Задержана'),
    )

    PRIORITY_CHOICES = (
        ('LOW', 'Низкий'),
        ('MEDIUM', 'Средний'),
        ('HIGH', 'Высокий'),
        ('URGENT', 'Срочный'),
    )

    cargo_type = models.ForeignKey(
        CargoType,
        on_delete=models.PROTECT,
        verbose_name='Тип груза'
    )
    weight = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Вес (т)')
    volume = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Объем (м³)')
    description = models.TextField(blank=True, verbose_name='Описание груза')

    origin_warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name='origin_shipments',
        verbose_name='Склад отправления'
    )
    destination_warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name='destination_shipments',
        verbose_name='Склад назначения'
    )

    planned_departure = models.DateTimeField(verbose_name='Плановое время отправления')
    planned_arrival = models.DateTimeField(verbose_name='Плановое время прибытия')
    actual_departure = models.DateTimeField(null=True, blank=True, verbose_name='Фактическое время отправления')
    actual_arrival = models.DateTimeField(null=True, blank=True, verbose_name='Фактическое время прибытия')

    assigned_vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Назначенный транспорт'
    )
    assigned_driver = models.ForeignKey(
        Driver,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Назначенный водитель'
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANNED', verbose_name='Статус')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM', verbose_name='Приоритет')

    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='created_shipments',
        verbose_name='Кем создана'
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_shipments',
        verbose_name='Кем назначена'
    )

    special_instructions = models.TextField(blank=True, verbose_name='Особые указания')
    delay_reason = models.TextField(blank=True, verbose_name='Причина задержки')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Поставка'
        verbose_name_plural = 'Поставки'
        ordering = ['-created_at']

    def clean(self):
        if self.planned_arrival <= self.planned_departure:
            raise ValidationError({
                'planned_arrival': 'Время прибытия должно быть позже времени отправления'
            })

        if self.origin_warehouse == self.destination_warehouse:
            raise ValidationError({
                'destination_warehouse': 'Склад назначения не может совпадать со складом отправления'
            })

        if self.assigned_vehicle and self.assigned_driver:
            if self.assigned_driver.vehicle != self.assigned_vehicle:
                raise ValidationError({
                    'assigned_driver': 'Водитель не привязан к назначенному транспортному средству'
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Поставка #{self.id} - {self.cargo_type.name}"

    def calculate_duration(self):
        if self.actual_departure and self.actual_arrival:
            return self.actual_arrival - self.actual_departure
        return None

    def is_delayed(self):
        if self.status == 'DELAYED':
            return True
        if self.planned_arrival and self.actual_arrival:
            return self.actual_arrival > self.planned_arrival
        return False


