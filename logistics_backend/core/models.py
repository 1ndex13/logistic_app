from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('LOGISTICS_MANAGER', 'Логист'),
        ('DISPATCHER', 'Диспетчер'),
        ('DRIVER', 'Водитель')
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='DRIVER', verbose_name='Роль')
    phone_number = models.CharField(max_length=11, blank=True, null=True, verbose_name='Номер телефона')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


