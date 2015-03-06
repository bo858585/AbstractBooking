from django.conf.urls import patterns, url
from django.contrib import admin
from .views import BookingCreate, BookingListView, serve_booking_view,\
    complete_booking_view, OwnBookingListView, DeleteBookingView,\
    approve_performer_view, reject_performer_view, UpdateBookingView,\
    BookingDetailView, CreateCommentView


admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^create_booking/', BookingCreate.as_view(),
                           name='create-booking'),
                       url(r'^booking_list/$', BookingListView.as_view(),
                           name='booking-list'),
                       url(r'^serve/$', serve_booking_view,
                           name='serve-booking'),
                       url(r'^approve_booking/$', approve_performer_view,
                           name='approve-booking'),
                       url(r'^reject_performer/$', reject_performer_view,
                           name='decline-booking'),
                       url(r'^complete/$', complete_booking_view,
                           name='complete-booking'),
                       url(r'^own_booking_list/$', OwnBookingListView.as_view(),
                           name='own-booking-list'),
                       url(r'^delete_booking/(?P<pk>\d+)/$', DeleteBookingView.as_view(),
                           name='delete-booking'),
                       url(r'^update_booking/(?P<pk>\d+)/$', UpdateBookingView.as_view(),
                           name='update-booking'),
                       url(r'^booking_detail/(?P<pk>\d+)/$', BookingDetailView.as_view(),
                           name='booking-detail'),
                       url(r'^create_comment/$', CreateCommentView.as_view(),
                           name='create-comment'),
                       )
