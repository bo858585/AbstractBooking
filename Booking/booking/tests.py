from django.test import TestCase
from booking.models import Booking
from django.contrib.auth.models import User


class BookingModelsTestCase(TestCase):
    def setUp(self):
        user1 = User.objects.create_user(
            'john', 'lennon@thebeatles.com', 'johnpassword'
        )
        user1.save()
        user2 = User.objects.create_user(
            'johndow', 'johndow@test.com', 'dowpassword'
        )
        user2.save()
        Booking.objects.create(
            title="test_booking",
            text="test_booking_text",
            price=150,
            customer=user1
        )

    def test_booking_processing(self):
        """Checks that booking can be assigned to the performer"""
        booking = Booking.objects.get(title='test_booking')
        user = User.objects.get(username='johndow')
        booking.set_performer(user)
        booking.save()
        booking = Booking.objects.get(title='test_booking')
        self.assertEqual(booking.performer, user)
        booking.complete()
        booking.save()
        self.assertEqual(booking.status, Booking.COMPLETED)


class TestBooking(TestCase):
    def test_call_view_without_being_logged_in(self):
        response = self.client.get('/booking/create_booking/', follow=True)
        self.assertRedirects(response, '/accounts/login/?next=/booking/create_booking/')
        response = self.client.get('/booking/booking_list/', follow=True)
        self.assertRedirects(response, '/accounts/login/?next=/booking/booking_list/')
        response = self.client.get('/home/', follow=True)
        self.assertEqual(response.status_code, 200)
