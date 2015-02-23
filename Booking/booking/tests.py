# -*- coding: utf-8 -*-

from django.test import TestCase
from booking.models import Booking, SystemAccount, UserProfile
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType


class BookingModelTestCase(TestCase):
    def setUp(self):
        # Создание пользователей
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


        # Создание группы с правами
        booking_content = ContentType.objects.get_for_model(Booking)

        customers, is_created = Group.objects.get_or_create(name="customers")
        add = Permission.objects.create(name="Can add", codename="can_add", content_type=booking_content)
        change = Permission.objects.create(name="Can change", codename="can_change", content_type=booking_content)
        delete = Permission.objects.create(name="Can delete", codename="can_delete", content_type=booking_content)

        customers.permissions.add(add)
        customers.permissions.add(change)
        customers.permissions.add(delete)
        customers.save()

        self.assertEqual(len(customers.permissions.all()), 3)
        self.assertEqual(customers.permissions.all()[0], add)
        self.assertEqual(customers.permissions.all()[1], change)
        self.assertEqual(customers.permissions.all()[2], delete)


        # Назначение пользователю группы
        user1.groups.add(customers)
        user1.save()

        self.assertEqual(len(user1.groups.all()), 1)
        self.assertEqual(user1.groups.all()[0], customers)


        # Создание группы с правами
        performers, is_created = Group.objects.get_or_create(name="performers")
        perform = Permission.objects.create(name="Can perform",
            codename="perform", content_type=booking_content)

        performers.permissions.add(perform)
        performers.save()

        self.assertEqual(len(performers.permissions.all()), 1)
        self.assertEqual(performers.permissions.all()[0], perform)


        # Назначение пользоателю группы
        user2.groups.add(performers)
        user2.save()

        self.assertEqual(len(user2.groups.all()), 1)
        self.assertEqual(user2.groups.all()[0], performers)

    def test_booking_processing(self):
        """Checks that booking can be assigned to the performer"""
        booking = Booking.objects.get(title='test_booking')

        self.assertEqual(booking.get_status(), Booking.PENDING)

        user1 = User.objects.get(username='john')
        booking.set_customer(user1)
        booking.save()

        self.assertEqual(booking.get_customer(), user1)

        user2 = User.objects.get(username='johndow')
        booking.set_performer(user2)
        booking.save()

        self.assertEqual(booking.get_status(), Booking.RUNNING)
        self.assertEqual(booking.get_performer(), user2)

        booking.complete()
        booking.save()

        self.assertEqual(booking.get_status(), Booking.COMPLETED)


class BookingViewsTestCase(TestCase):
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
