from django.db import models
from django.core.exceptions import ValidationError
from core.models import User

class Warehouse(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название склада')
    address = models.TextField(verbose_name='Адрес')
    capacity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Вместимость (м³)')
    current_load = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Текущая загрузка (м³)')
    specialization = models.TextField(blank=True, verbose_name='Специализация')
    working_hours = models.TextField(blank=True, verbose_name='Режим работы')
    contact_person = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Ответственное лицо',
        related_name='warehouses',
        limit_choices_to={'role__in': ['LOGISTICS_MANAGER', 'DISPATCHER']}
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name='Широта')
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name='Долгота')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Склад'
        verbose_name_plural = 'Склады'

    def clean(self):
        if self.contact_person and self.contact_person.role not in ['LOGISTICS_MANAGER', 'DISPATCHER']:
            raise ValidationError({
                'contact_person': 'Ответственным лицом может быть только Логист или Диспетчер'
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def utilization_percentage(self):
        if self.capacity > 0:
            return round((self.current_load / self.capacity) * 100, 2)
        return 0