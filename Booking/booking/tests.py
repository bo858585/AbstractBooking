# -*- coding: utf-8 -*-

from django.test import TestCase
from booking.models import Booking, SystemAccount, UserProfile
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
        SystemAccount.objects.create()
        UserProfile.objects.create(user=user1)
        UserProfile.objects.create(user=user2)

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
    def setUp(self):
        pass

    def test_calling_view_without_being_logged_in(self):
        response = self.client.get('/booking/create_booking/', follow=True)
        self.assertRedirects(response, '/accounts/login/?next=/booking/create_booking/')
        response = self.client.get('/booking/booking_list/', follow=True)
        self.assertRedirects(response, '/accounts/login/?next=/booking/booking_list/')
        response = self.client.get('/home/', follow=True)
        self.assertEqual(response.status_code, 200)


    def test_create_customer_and_performer_create_booking_and_serve(self):
        """
        Создать двух пользователей - заказчик и исполнитель. Один создает заказ.
        Другой берет его на выполнение. Первый завершает заказ.
        """
        pass

    def test_create_three_users_create_booking_and_2nd_customer_can_not_serve(self):
        """
        Создать трех пользователей - два заказчика и исполнитель.
        Заказчик создает заказ. Исполнитель берет на обслуживание.
        Второй заказчик не должен смочь его завершить.
        """
        pass

    def test_performer_can_not_perform_booking_of_other_performer(self):
        """
        Создать двух пользователей - заказчик и заказчик. Один создает заказ.
        Второму не хватает прав для взятия не выполнение.
        """
        pass

    def test_performer_and_can_not_create_booking(self):
        """
        Создать пользователя - исполнитель.
        Ему должно не хватать прав для создания заказа.
        """
        pass
