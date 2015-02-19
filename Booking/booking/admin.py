from django.contrib import admin
from .models import UserProfile
from .models import Booking

admin.site.register(Booking)
admin.site.register(UserProfile)
