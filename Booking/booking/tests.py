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

    def test_booking_processing(self):
        """
        Создание двух пользователей: исполнитель и заказчик.
        Создание заказа.
        Назначение заказу заказчика.
        Назначание заказу исполнителя.
        Исполнение заказа.
        Проверка статусов заказа в ходе этих назначений.
        Проверка назначенности заказу пользователей в ходе этих назначений.
        """

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
        """
        Создание пользователей: заказчик, исполнитель.
        Назначение им прав на создание исполнение заказа соответсвенно.
        """
        user1 = User.objects.create_user(
            'john', 'lennon@thebeatles.com', 'johnpassword'
        )
        user1.save()
        user2 = User.objects.create_user(
            'johndow', 'johndow@test.com', 'dowpassword'
        )
        user2.save()
        SystemAccount.objects.create()
        UserProfile.objects.create(user=user1, cash=20.00)
        UserProfile.objects.create(user=user2, cash=0.00)

        content_type = ContentType.objects.get_for_model(Booking)
        permission = Permission.objects.create(content_type=content_type, codename='add_booking')
        user1.user_permissions.add(permission)
        user1.save()

        permission = Permission.objects.get(content_type=content_type, codename='perform_perm')
        user2.user_permissions.add(permission)
        user2.save()

    def test_calling_view_without_being_logged_in(self):
        response = self.client.get('/booking/create_booking/', follow=True)
        self.assertRedirects(response, '/accounts/login/?next=/booking/create_booking/')
        response = self.client.get('/booking/booking_list/', follow=True)
        self.assertRedirects(response, '/accounts/login/?next=/booking/booking_list/')
        response = self.client.get('/home/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'homepage.html')

    def test_create_customer_and_performer_create_booking_and_serve(self):
        """
        Заказчик создает заказ.
        Другой берет его на выполнение.
        Первый завершает заказ.
        """

        user1 = User.objects.get(username='john')
        user1_cash_before = user1.profile.cash

        # Вход
        response = self.client.post('/accounts/login/',
            {'username': 'john', 'password': 'johnpassword'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'homepage.html')

        # Просмотр списка заказов
        response = self.client.get('/booking/booking_list/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking/booking_list.html')

        # Просмотр формы создания заказа
        response = self.client.get('/booking/create_booking/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking/booking_form.html')

        # Создание заказа
        response = self.client.post('/booking/create_booking/',
                {'title': 'test_title1', 'text': 'test_text1', 'price': '12.00' },
                follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking/booking_list.html')

        # Проверка того, что заказ в базе после создания
        self.assertEqual(len(Booking.objects.all()), 1)
        booking = Booking.objects.all()[0]

        user1 = User.objects.get(username='john')

        self.assertEqual(booking.get_customer(), user1)
        self.assertEqual(booking.title, 'test_title1')
        self.assertEqual(booking.text, 'test_text1')
        self.assertEqual(booking.price, 12.0)
        self.assertEqual(booking.status, Booking.PENDING)

        # Выход
        response = self.client.post('/accounts/logout/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/logged_out.html')


        # Вход из-под исполнителя
        response = self.client.post('/accounts/login/',
            {'username': 'johndow', 'password': 'dowpassword'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'homepage.html')

        user2 = User.objects.get(username='johndow')

        # Просмотр списка заказов
        response = self.client.get('/booking/booking_list/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking/booking_list.html')

        # Взятие заказа на исполнение
        response = self.client.post('/booking/serve/',
            { 'booking': booking.id }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking/booking_list.html')

        # Взят на исполнение
        booking = Booking.objects.all()[0]
        self.assertEqual(booking.get_performer(), user2)
        self.assertEqual(booking.get_status(), Booking.RUNNING)

        self.assertEqual(user1.profile.cash + booking.price, user1_cash_before)

        # Выход
        response = self.client.post('/accounts/logout/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/logged_out.html')


        # Вход из-под заказчика
        response = self.client.post('/accounts/login/',
            {'username': 'john', 'password': 'johnpassword'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'homepage.html')

        user = User.objects.get(username='john')

        # Закрытие заказа
        response = self.client.post('/booking/complete/',
            { 'booking': booking.id }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking/booking_list.html')

        # Взят на исполнение
        booking = Booking.objects.all()[0]
        self.assertEqual(booking.get_status(), Booking.COMPLETED)
        system_account = SystemAccount.objects.all()[0]
        comission = system_account.get_comission()
        self.assertEqual(system_account.account, booking.price*comission)
        self.assertEqual(user2.profile.cash, booking.price*(1 - comission))

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
