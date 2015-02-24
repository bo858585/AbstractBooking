from django.conf.urls import patterns, url
from django.contrib import admin
from .views import BookingCreate, BookingListView, serve_booking_view,\
    complete_booking_view

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^create_booking/', BookingCreate.as_view(),
                           name='create-booking'),
                       url(r'^booking_list/$', BookingListView.as_view(),
                           name='booking-list'),
                       url(r'^serve/$', serve_booking_view,
                           name='serve-booking'),
                       url(r'^complete/$', complete_booking_view,
                           name='complete-booking'),
                       )
