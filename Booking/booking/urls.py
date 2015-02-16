from django.conf.urls import patterns, url
from django.contrib import admin
from .views import BookingCreate, BookingListView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^create_booking/', BookingCreate.as_view(), name='create-booking'),
    url(r'^booking_list/$', BookingListView.as_view(), name='booking-list'),
)
