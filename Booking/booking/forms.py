# -*- coding: utf-8 -*-

from django.forms import ModelForm
from .models import Booking
from django import forms


class BookingForm(ModelForm):

    """
    Форма для создания заказа
    """
    class Meta:
        model = Booking
        fields = ['title', 'text', 'price']
