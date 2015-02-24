# -*- coding: utf-8 -*-

"""
Формы заказов
"""

from django.forms import ModelForm
from .models import Booking


class BookingForm(ModelForm):

    """
    Форма для создания заказа
    """
    class Meta:
        model = Booking
        fields = ['title', 'text', 'price']
