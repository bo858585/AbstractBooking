# -*- coding: utf-8 -*-

"""
Регистрация моделей в админке
"""

from django.contrib import admin
from .models import UserProfile
from .models import Booking
from .models import SystemAccount

admin.site.register(Booking)
admin.site.register(UserProfile)
admin.site.register(SystemAccount)
