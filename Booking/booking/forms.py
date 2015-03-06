# -*- coding: utf-8 -*-

"""
Формы заказов
"""

from django.forms import ModelForm
from .models import Booking, Comment


class BookingForm(ModelForm):

    """
    Форма для создания заказа
    """
    class Meta:
        model = Booking
        fields = ['title', 'text', 'price']


class CommentForm(ModelForm):

    """
    Форма для создания заказа
    """
    class Meta:
        model = Comment
        fields = ['text']
