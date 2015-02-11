# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Booking(models.Model):
    """Booking"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"

    STATUS_CHOICES = (
        (PENDING, u"Ожидает выполнения" ),
        (RUNNING, u"Взят на исполнение" ),
        (COMPLETED, u"Завершен" ),
    )

    title = models.CharField(max_length=50)
    text = models.TextField(max_length=200)
    price = models.IntegerField(default=100)
    status = models.CharField(
        choices=STATUS_CHOICES,
        default=PENDING,
        max_length=30
    )
    customer = models.ForeignKey(User, related_name='customer_booking')
    performer = models.ForeignKey(User, null=True, related_name='performer_booking')
    date = models.DateTimeField(auto_now_add=True)

    def set_performer(self, performer):
        self.performer = performer
