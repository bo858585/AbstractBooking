# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.db import models

from decimal import Decimal


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
        """
        Установка исполнителя для заказа. Установка выполняющегося статуса для заказа.
        """
        self.performer = performer
        self.status = self.RUNNING
        self.save()

    def get_customer(self):
        return self.customer

    def complete(self):
        """
        Перевод средств со счета заказчика на счет исполнителя.
        Перевод средств со счета заказчика на счет исполнителя.
        Установка завершающего статуса для заказа.
        """
        system_account = SystemAccount.objects.all()[0]
        comission = system_account.get_comission()
        cash_for_system = self.price*comission
        cash_for_performer = self.price*(1 - comission)
        print comission, cash_for_system, cash_for_performer
        print system_account.account
        system_account.transfer_cash(cash_for_system)
        system_account.save()
        print system_account.account
        print self.performer.profile.cash
        self.performer.profile.increase_cash(cash_for_performer)
        self.performer.profile.save()
        print self.performer.profile.cash
        self.status = self.COMPLETED
        self.save()

    def get_status(self):
        """
        Получение текущего статуса заказа
        """
        return self.status


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile')
    cash = models.DecimalField(max_digits=6, decimal_places=2)

    def __unicode__(self):
        return self.user.username

    def increase_cash(self, _cash):
        self.cash += _cash

    def decrease_cash(self, _cash):
        self.cash -= _cash

    def has_enough_cash_for_booking(self, price):
        """
        Цена введенного заказа должна быть меньше (либо равна) сумме,
        которая заказчика есть на счету
        """
        if self.cash >= price:
            return True
        else:
            return False


class SystemAccount(models.Model):
    account = models.DecimalField(max_digits=6, decimal_places=2,
        default=Decimal('0.00'))
    commission = models.DecimalField(max_digits=3, decimal_places=2,
        default=Decimal('0.03'))

    def transfer_cash(self, _cash):
        self.account += _cash

    def get_comission(self):
        return self.commission
