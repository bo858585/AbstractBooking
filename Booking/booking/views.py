# -*- coding: utf-8 -*-

"""
Views для работы с заказами
"""

from django.views.generic.edit import CreateView
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import permission_required
from django.views.generic.list import ListView
from django.http import HttpResponse
from django.db import transaction
from django.contrib import messages
from django.db import DatabaseError
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import user_passes_test

from .models import Booking
from .forms import BookingForm
from Booking.views import LoginRequiredMixin

import json


class BookingCreate(LoginRequiredMixin, CreateView):
    """
    Создание заказа
    """
    model = Booking
    fields = ['title', 'text', 'price']
    form_class = BookingForm
    success_url = "/booking/booking_list/"

    @method_decorator(login_required)
    @method_decorator(permission_required('booking.add_booking',
        raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(BookingCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.set_customer(self.request.user)
        return HttpResponseRedirect(self.get_success_url())


class BookingListView(LoginRequiredMixin, ListView):

    """
    В начале на заказе есть кнопка “Взять заказ”, которая отображается только
    исполнителям.
    Завершенные заказы не отображаются.

    Соответствие надписей на кнопках заказа из последнего столбца таблицы и
    текущих статусов этих заказов:
     (Надпись на кнопке - статус заказа):

    - "Взять заказ"("can_take") отображается только для исполнителей -
    заказ ожидает выполнения(статус "pending").

    - "Завершить заказ" ("can_complete") - только для пользователя, создавшего
    заказ - заказ "Взят на исполнение"(статус "running").

    - Заказ не отображается в таблице - “Завершен”(статус "completed").
    """
    model = Booking
    paginate_by = 20
    queryset = Booking.objects.exclude(
        status__exact=Booking.COMPLETED).order_by('-date')

    CAN_COMPLETE = "can_complete"
    CAN_TAKE = "can_take"
    CAN_VIEW = "can_view"

    def get_context_data(self, **kwargs):
        context = super(BookingListView, self).get_context_data(**kwargs)
        permissions_list = []
        user = self.request.user

        for o in context['object_list']:
            # Заказ ждет выполнения
            if o.status == Booking.PENDING:
                if not user.has_perm("booking.add_booking"):
                    # Тип пользователя - исполнитель.
                    # Такие пользователи могут брать заказы на выполнение.
                    permissions_list.append(self.CAN_TAKE)
                else:
                    # Остальные могут просматривать
                    permissions_list.append(self.CAN_VIEW)
            else:
                # Заказ кем-то исполняется
                if o.status == Booking.RUNNING:
                    # Текущий пользователь создавал этот заказ.
                    if o.customer == user:
                        # Такой пользователь может завершать заказ.
                        permissions_list.append(self.CAN_COMPLETE)
                    else:
                        # Иначе - только просматривать
                        permissions_list.append(self.CAN_VIEW)
                else:
                    if o.status == Booking.COMPLETED:
                        # Если заказ завершен, его можно только просматривать.
                        permissions_list.append(self.CAN_VIEW)

        context['bookings'] = zip(context['object_list'], permissions_list)

        return context


@login_required
@user_passes_test(lambda u: u.has_perm('booking.perform_perm'))
def serve_booking_view(request):
    """
    При клике исполнителя (performer) на кнопку “Взять заказ” производится
    проверка, хватит ли заказчику этого заказа (customer) денег на оплату
    заказа. Если хватит, со счета заказчика списывается цена заказа. Заказу
    назначается статус “Выполняется”. Заказ сохраняется. Эти операции - в одной
    транзакции. (это значит, что системе в ленту заказов - виртульно, согласно
    статусу заказа - перешли деньги со счета заказчика, то есть система
    выступает посредником между заказчиком и исполнителем). Страница
    обновляется. Кнопка “Взять заказ” на заказе исчезает, появляется кнопка
    “Завершить заказ”, доступная только заказчику, сделавшему этот заказ.
    """
    if request.method == "POST":
        if request.is_ajax():
            try:
                with transaction.atomic():
                    # Проверка текущего статуса заказа
                    booking = Booking.objects.get(id=request.POST['id'])
                    booking_status = booking.get_status()
                    if booking_status != Booking.PENDING:
                        status_message = u"Неверный статус заказа"
                    else:
                        customer = booking.get_customer()
                        try:
                            is_enough_cash = \
                                customer.profile.has_enough_cash_for_booking(
                                    booking.price
                                )
                        except ObjectDoesNotExist:
                            status_message = \
                                u'У создателя заказа нет расширенного профиля'
                            return HttpResponse(json.dumps({'request_status':
                                status_message}),
                                content_type="application/json")
                        # Проверка средств на счету пользователя.
                        if is_enough_cash:
                            # Их вычет со счета. И назначение заказу исполнителя
                            customer.profile.decrease_cash(booking.price)
                            customer.profile.save()
                            status_message = Booking.RUNNING
                            booking.set_performer(request.user)
                            status_message = u"Деньги перешли на счет системы"
                        else:
                            status_message = u"Недостаточно средств"
            except DatabaseError:
                # Проблема с generating relationships
                status_message = u'Внутренняя ошибка'
            return HttpResponse(json.dumps({'request_status': status_message}),
                                content_type="application/json")
        else:
            try:
                with transaction.atomic():
                    booking = Booking.objects.get(id=request.POST['booking'])
                    booking_status = booking.get_status()
                    if booking_status != Booking.PENDING:
                        messages.error(request, u'Неверный статус заказа')
                    else:
                        customer = booking.get_customer()
                        is_enough_cash = \
                            customer.profile.has_enough_cash_for_booking(
                                booking.price
                            )
                        if is_enough_cash:
                            customer.profile.decrease_cash(booking.price)
                            customer.profile.save()
                            messages.info(
                                request, u'Деньги перешли на счет системы')
                            booking.set_performer(request.user)
                        else:
                            messages.error(request, u'Недостаточно средств')
            except DatabaseError:
                messages.error(request, u'Внутренняя ошибка')
            return HttpResponseRedirect("/booking/booking_list/")
    return HttpResponse("")


@login_required
@permission_required('booking.add_booking', raise_exception=True)
def complete_booking_view(request):
    """
    При нажатии на кнопку “Завершить заказ” сумма заказа в ленте в зависимости
    от комиссии (целое число от 0 до 100 процентов, указывается в админке)
    делится на две части - на счет исполнителя заказа и системы поступают две
    эти части суммы. Заказу назначается статус “Завершен”. Страница обновляется.
    Заказ исчезает из ленты как выполнившийся.
    """
    if request.method == "POST":
        if request.is_ajax():
            try:
                with transaction.atomic():
                    booking = Booking.objects.get(id=request.POST['id'])
                    booking_status = booking.get_status()
                    if booking_status != Booking.RUNNING:
                        status_message = u"Неверный статус заказа"
                    else:
                        booking_customer = booking.get_customer()
                        if booking_customer != request.user:
                            status_message = u"Это не ваш заказ"
                        else:
                            status_message = u"Заказ завершен"
                            booking.complete()
            except DatabaseError:
                # Проблема с generating relationships
                status_message = u'Внутренняя ошибка'
            return HttpResponse(json.dumps({'request_status': status_message}),
                                content_type="application/json")
        else:
            try:
                with transaction.atomic():
                    booking = Booking.objects.get(id=request.POST['booking'])
                    booking_status = booking.get_status()
                    if booking_status != Booking.RUNNING:
                        messages.error(request, u'Неверный статус заказа')
                    else:
                        booking_customer = booking.get_customer()
                        if booking_customer != request.user:
                            status_message = \
                                u"Не этот пользователь создавал заказ"
                            messages.error(request, status_message)
                        else:
                            messages.info(request, u'Заказ завершен')
                            booking.complete()
            except DatabaseError:
                messages.error(request, u'Внутренняя ошибка')
            return HttpResponseRedirect("/booking/booking_list/")

    return HttpResponse("")
