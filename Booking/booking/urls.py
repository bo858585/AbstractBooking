from django.conf.urls import patterns, url

from .views import BookingCreate

urlpatterns = patterns('',
    url(r'^create_booking/', BookingCreate.as_view(), name='index'),
)
