# -*- coding: utf-8 -*-

"""
Модели
"""

from django.db import models
from django.contrib.auth.models import User

from decimal import Decimal


# Create your models here.

class Booking(models.Model):

    """Модель заказа"""

    class Meta:
        """
        Права по-умолчанию обнулены.
        Добавлено право на исполнение заказа.
        """
        default_permissions = ()
        permissions = (
            ("perform_perm", u"Ability to perform created booking"),
        )

    PENDING = "pending"
    WAITING_FOR_APPROVAL = "waiting_for_approval"
    RUNNING = "running"
    COMPLETED = "completed"

    STATUS_CHOICES = (
        (PENDING, u"Ожидает исполнителя"),
        (WAITING_FOR_APPROVAL, u"Ожидает подтверждения заказчиком"),
        (RUNNING, u"Взят на исполнение"),
        (COMPLETED, u"Завершен"),
    )

    title = models.CharField(max_length=100)
    text = models.TextField(max_length=4000)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=100)
    status = models.CharField(
        choices=STATUS_CHOICES,
        default=PENDING,
        max_length=30
    )
    customer = models.ForeignKey(User, related_name='customer_booking')
    performer = models.ForeignKey(
        User, null=True, blank=True, related_name='performer_booking')
    date = models.DateTimeField(auto_now_add=True)

    def set_performer(self, performer):
        """
        Установка исполнителя для заказа. Установка выполняющегося статуса
        для заказа.
        """
        self.performer = performer
        self.save()

    def set_customer(self, customer):
        """
        Установка заказчика для заказа.
        """
        self.customer = customer
        self.save()

    def get_customer(self):
        """
        Получение модели исполнителя
        """
        return self.customer

    def get_performer(self):
        """
        Получение модели исполнителя
        """
        return self.performer

    def complete(self):
        """
        Перевод средств со счета заказчика на счет исполнителя.
        Установка завершающего статуса для заказа.
        """
        system_account = SystemAccount.objects.all()[0]
        comission = system_account.get_comission()
        cash_for_system = self.price * comission
        cash_for_performer = self.price * (1 - comission)
        system_account.transfer_cash(cash_for_system)
        system_account.save()
        self.performer.profile.increase_cash(cash_for_performer)
        self.performer.profile.save()
        self.status = self.COMPLETED
        self.save()
        return cash_for_system, cash_for_performer

    def get_status(self):
        """
        Получение текущего статуса заказа
        """
        return self.status

    def set_status(self, status):
        """
        Установка статуса для заказа.
        """
        self.status = status
        self.save()


class UserProfile(models.Model):
    """
    Расширенный профиль пользователя
    """
    user = models.OneToOneField(User, related_name='profile')
    cash = models.DecimalField(
        max_digits=6, decimal_places=2, default=Decimal('0.0'))

    def __unicode__(self):
        return self.user.username

    def increase_cash(self, _cash):
        """
        Увеличение денег на счету пользователя.
        """
        self.cash += _cash

    def decrease_cash(self, _cash):
        """
        Уменьшение денег на счету пользователя.
        """
        self.cash -= _cash

    def has_enough_cash_for_booking(self, price):
        """
        Цена введенного заказа должна быть меньше (либо равна) сумме,
        которая заказчика есть на счету, для того, чтобы он мог оплатить заказ.
        Проверяется при взятии заказа исполнителем.
        """
        if self.cash >= price:
            return True
        else:
            return False


class SystemAccount(models.Model):

    """
    Счет системы, на который происходит перевод процента-комиссии цены заказа
    со счета заказа после его завершения.
    """
    account = models.DecimalField(max_digits=6, decimal_places=2,
                                  default=Decimal('0.00'))
    commission = models.DecimalField(max_digits=3, decimal_places=2,
                                     default=Decimal('0.03'))

    def transfer_cash(self, _cash):
        """
        Пополнение средств на счету
        """
        self.account += _cash

    def get_comission(self):
        """
        Комиссия системы
        """
        return self.commission
