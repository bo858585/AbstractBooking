# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Booking(models.Model):
    """Booking"""
    class Meta:
    	default_permissions = ()

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"

    STATUS_CHOICES = (
        (PENDING, u"Ожидает исполнителя" ),
        (RUNNING, u"Взят на исполнение" ),
        (COMPLETED, u"Завершен" ),
    )

    title = models.CharField(max_length=100)
    text = models.TextField(max_length=500)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=100)
    status = models.CharField(
        choices=STATUS_CHOICES,
        default=PENDING,
        max_length=30
    )
    customer = models.ForeignKey(User, related_name='customer_booking')
    performer = models.ForeignKey(User, null=True, blank=True, related_name='performer_booking')
    date = models.DateTimeField(auto_now_add=True)

    def set_performer(self, performer):
        self.performer = performer
