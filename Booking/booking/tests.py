from django.test import TestCase
from booking.models import Booking
from django.contrib.auth.models import User


class BookingTestCase(TestCase):
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
