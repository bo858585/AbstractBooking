# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import permission_required
from django.views.generic.list import ListView
from django.contrib.auth import get_user_model

from .models import Booking
from .forms import BookingForm
from Booking.views import LoginRequiredMixin


class BookingCreate(LoginRequiredMixin, CreateView):
    model = Booking
    fields = ['title', 'text', 'price']
    form_class = BookingForm
    success_url = "/booking/booking_list/"

    @method_decorator(login_required)
    @method_decorator(permission_required('booking.add_booking', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(BookingCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.customer = self.request.user
        self.object.save()
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

    - "Завершить заказ" ("can_complete") - только для пользователя, создавшего  заказ -
    заказ "Взят на исполнение"(статус "running").

    - Заказ не отображается в таблице - “Завершен”(статус "completed").
    """
    model = Booking
    paginate_by = 20
    queryset = Booking.objects.exclude(status__exact=Booking.COMPLETED).order_by('-date')

    CAN_COMPLETE = "can_complete"
    CAN_TAKE = "can_take"
    CAN_VIEW = "can_view"

    def get_context_data(self, **kwargs):
        context = super(BookingListView, self).get_context_data(**kwargs)
        permissions_list = []
        user = self.request.user

        for o in context['object_list']:
            # Заказ ждет выполнения и тип текущего пользователя - исполнитель.
            # Такие пользователи могут брать заказы на выполнение.

            if o.status == Booking.PENDING:
                if not user.has_perm("booking.add_booking"):
                    print 11
                    permissions_list.append(self.CAN_TAKE)
                else:
                    permissions_list.append(self.CAN_VIEW)#tested

            # Заказ кем-то исполняется и текущий пользователь создавал этот заказ.
            # Такой пользователь может завершать заказ.
            else:
                if o.status == Booking.RUNNING:
                    print o.customer, user
                    if o.customer == user:
                        permissions_list.append(self.CAN_COMPLETE)#
                    else:
                        permissions_list.append(self.CAN_VIEW)#tested
                else:
                    if o.status == Booking.COMPLETED:
                        # Если заказ завершен, его можно только просматривать.
                        permissions_list.append(self.CAN_VIEW)

        context['bookings'] = zip(context['object_list'], permissions_list)
        return context
