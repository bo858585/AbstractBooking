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
from django.views.generic.edit import DeleteView
from django.http import HttpResponse
from django.db import transaction
from django.contrib import messages
from django.db import DatabaseError
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.core.urlresolvers import reverse_lazy
from django.http import Http404
from django.views.generic.edit import UpdateView
from django.views.generic.detail import DetailView

from django.core.urlresolvers import reverse

from .models import Booking, Comment
from .forms import BookingForm, CommentForm
from Booking.views import LoginRequiredMixin

import json


class BookingCreate(CreateView):
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
    Список всех заказов.

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

    # Заказчик может завершить заказ
    CAN_COMPLETE = "can_complete"
    # Исполнитель может взять заказ
    CAN_TAKE = "can_take"
    # Возможность смотреть заказ
    CAN_VIEW = "can_view"
    # Кнопка взятия заказа неактивна
    NOT_ACTIVE = "not_active"
    # Заказчик может подтверждать/отклонять заказ
    CAN_APPROVE = "can_approve"

    def get_context_data(self, **kwargs):
        context = super(BookingListView, self).get_context_data(**kwargs)
        permissions_list = []
        user = self.request.user

        for o in context['object_list']:
            # Заказ ждет выполнения
            if o.status == Booking.PENDING:
                if not user.has_perm("booking.add_booking"):
                    # Тип пользователя - исполнитель.
                    if o.customer.profile.has_enough_cash_for_booking(o.price):
                        # Такие пользователи могут брать заказы на выполнение,
                        # если у заказчика достаточно средств
                        permissions_list.append(self.CAN_TAKE)
                    else:
                        # Иначе - кнопка взятия заказа неактивна
                        permissions_list.append(self.NOT_ACTIVE)
                else:
                    if o.customer.profile.has_enough_cash_for_booking(o.price):
                        # Остальные могут просматривать
                        permissions_list.append(self.CAN_VIEW)
                    else:
                        # Иначе - кнопка взятия заказа неактивна
                        permissions_list.append(self.NOT_ACTIVE)
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
                    else:
                        if o.status == Booking.WAITING_FOR_APPROVAL:
                            # Заказ ждет подтверждения заказчиком после попытки
                            # исполнителя его взять
                            if not user.has_perm("booking.add_booking"):
                                # Для исполнителя кнопка заказа неактивна
                                permissions_list.append(self.NOT_ACTIVE)
                            else:
                                # Заказчик может подтрверждать/отклонять,
                                # если создавал этот заказ
                                if o.customer == user:
                                    permissions_list.append(self.CAN_APPROVE)
                                else:
                                    permissions_list.append(self.CAN_VIEW)

        context['bookings'] = zip(context['object_list'], permissions_list)
        context['page_type'] = "all_bookings"

        return context


@login_required
@user_passes_test(lambda u: u.has_perm('booking.perform_perm'))
def serve_booking_view(request):
    """
    Исполнитель пытается взять заказ.

    При клике исполнителя (performer) на кнопку “Взять заказ” производится
    проверка, хватит ли заказчику этого заказа (customer) денег на оплату
    заказа. Если хватит, заказу назначается статус “Ожидает подтверждения”.
    Заказ сохраняется. Страница обновляется. Кнопка “Взять заказ”
    на заказе исчезает.
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
                            booking.set_performer(request.user)
                            booking.set_status(Booking.WAITING_FOR_APPROVAL)
                            status_message =\
                             u"Заявка на выполнение ожидает подтверждения заказчиком."
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
                            messages.info(
                                request, u"Заявка на выполнение ожидает подтверждения заказчиком.")
                            booking.set_performer(request.user)
                            booking.set_status(Booking.WAITING_FOR_APPROVAL)
                        else:
                            messages.error(request, u'Недостаточно средств')
            except DatabaseError:
                messages.error(request, u'Внутренняя ошибка')
            return HttpResponseRedirect("/booking/booking_list/")
    return HttpResponse("")


@login_required
@user_passes_test(lambda u: u.has_perm('booking.add_booking'))
def approve_performer_view(request):
    """
    Заказчик подтверждает исполнителю взятие заказа. Деньги переводятся на счет
    системы.

    При клике заказчика на кнопку “Подтвердить заказ” производится
    проверка, хватит ли заказчику этого заказа (customer) денег на оплату
    заказа. Если хватит, со счета заказчика списывается цена заказа. Заказу
    назначается статус “Выполняется”. Заказ сохраняется. Эти операции - в одной
    транзакции. (это значит, что системе в ленту заказов - виртуально, согласно
    статусу заказа - перешли деньги со счета заказчика, то есть система
    выступает посредником между заказчиком и исполнителем). Страница
    обновляется. Кнопки “Подтвердить/Отклонить заказ” на заказе исчезают, появляется кнопка
    “Завершить заказ”, доступная только заказчику, сделавшему этот заказ.
    """
    if request.method == "POST":
        if request.is_ajax():
            try:
                with transaction.atomic():
                    booking = Booking.objects.get(id=request.POST['booking_id'])

                    # Проверка того, что текущий пользователь создавал заказ
                    customer = booking.get_customer()
                    if request.user != customer:
                        status_message = u"Это не Ваш заказ"
                        return HttpResponse(json.dumps({'request_status':
                            status_message}),
                            content_type="application/json")

                    # Проверка текущего статуса заказа
                    booking_status = booking.get_status()
                    if booking_status != Booking.WAITING_FOR_APPROVAL:
                        status_message = u"Неверный статус заказа"
                    else:
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
                            booking.set_status(Booking.RUNNING)
                            status_message = u"Заказ в обработке. Деньги перешли от заказчика на временный системный счет."
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

                    # Проверка того, что текущий пользователь создавал заказ
                    customer = booking.get_customer()
                    if request.user != customer:
                        messages.error(request, u'Это не Ваш заказ')
                        return HttpResponseRedirect("/booking/booking_list/")

                    booking_status = booking.get_status()
                    if booking_status != Booking.WAITING_FOR_APPROVAL:
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
                                request, u"Заказ в обработке. Деньги перешли от заказчика на временный системный счет.")
                            booking.set_status(Booking.RUNNING)
                        else:
                            messages.error(request, u'Недостаточно средств')
            except DatabaseError:
                messages.error(request, u'Внутренняя ошибка')
            return HttpResponseRedirect("/booking/booking_list/")
    return HttpResponse("")


@login_required
@user_passes_test(lambda u: u.has_perm('booking.add_booking'))
def reject_performer_view(request):
    """
    Заказчик отклоняет попытку исполнителя взять его заказ.

    Статус заказа становится “Ожидает выполнения”. Удалять заказ теперь можно.
    Как и подавать заявку на исполнение - любой исполнитель может это сделать.
    """
    if request.method == "POST":
        if request.is_ajax():
            try:
                with transaction.atomic():
                    # Проверка текущего статуса заказа
                    booking = Booking.objects.get(id=request.POST['booking_id'])

                    # Проверка того, что текущий пользователь создавал заказ
                    customer = booking.get_customer()
                    if request.user != customer:
                        status_message = u"Это не Ваш заказ"
                        return HttpResponse(json.dumps({'request_status':
                            status_message}),
                        content_type="application/json")

                    booking_status = booking.get_status()
                    if booking_status != Booking.WAITING_FOR_APPROVAL:
                        status_message = u"Неверный статус заказа"
                    else:
                        booking.set_performer(None)
                        booking.set_status(Booking.PENDING)
                        status_message = u"Заказ ожидает выполнения."
            except DatabaseError:
                # Проблема с generating relationships
                status_message = u'Внутренняя ошибка'
            return HttpResponse(json.dumps({'request_status': status_message}),
                                content_type="application/json")
        else:
            try:
                with transaction.atomic():
                    booking = Booking.objects.get(id=request.POST['booking'])

                    # Проверка того, что текущий пользователь создавал заказ
                    customer = booking.get_customer()
                    if request.user != customer:
                        messages.error(request, u'Это не Ваш заказ')
                        return HttpResponseRedirect("/booking/booking_list/")

                    booking_status = booking.get_status()
                    if booking_status != Booking.WAITING_FOR_APPROVAL:
                        messages.error(request, u'Неверный статус заказа')
                    else:
                        booking.set_performer(None)
                        booking.set_status(Booking.PENDING)
                        status_message = u"Заказ ожидает выполнения."
            except DatabaseError:
                messages.error(request, u'Внутренняя ошибка')
            return HttpResponseRedirect("/booking/booking_list/")
    return HttpResponse("")


@login_required
@permission_required('booking.add_booking', raise_exception=True)
def complete_booking_view(request):
    """
    Перевод средств со счета системы на счет исполнителя заказчиком и
    завершение заказа.

    Сумма заказа в ленте в зависимости от комиссии (целое число от 0 до 100
    процентов, указывается в админке с системном счете) делится на две части -
    на счет исполнителя заказа (виден пользователю на его странице) и системы
    (SystemAccount в админке) поступают две эти части суммы. Заказу назначается
    статус “Завершен”. Заказчику выводятся сообщения с указанием этих сумм.
    Страница обновляется. Заказ исчезает из ленты как выполнившийся.
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
                            cash_for_system, cash_for_performer = booking.complete()
                            status_message = \
                            (u"Заказ завершен. С суммы заказа считана комиссия"
                       u" в размере %(cash_for_system)g. %(cash_for_performer)g"
                            u" переведено исполнителю.") % {
                            'cash_for_system': cash_for_system,
                            'cash_for_performer': cash_for_performer }

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
                            cash_for_system, cash_for_performer = booking.complete()
                            status_message = \
                            (u"Заказ завершен. С суммы заказа считана комиссия"
                       u" в размере %(cash_for_system)g. %(cash_for_performer)g"
                            u" переведено исполнителю.") % {
                            'cash_for_system': cash_for_system,
                            'cash_for_performer': cash_for_performer }
                            messages.info(request, status_message)
            except DatabaseError:
                messages.error(request, u'Внутренняя ошибка')
            return HttpResponseRedirect("/booking/booking_list/")

    return HttpResponse("")


class OwnBookingListView(LoginRequiredMixin, ListView):
    """
    Список заказов самого пользователя
    """

    CAN_COMPLETE = "can_complete"
    CAN_TAKE = "can_take"
    CAN_VIEW = "can_view"
    # Кнопка взятия заказа неактивна
    NOT_ACTIVE = "not_active"
    # Заказчик может подтверждать/отклонять заказ
    CAN_APPROVE = "can_approve"

    model = Booking
    paginate_by = 20
    template_name = 'booking/booking_list.html'

    def get_queryset(self):
        queryset = Booking.objects.filter(
            Q(customer=self.request.user) | Q(performer=self.request.user)
        ).order_by('-date')
        return queryset

    def get_context_data(self, **kwargs):
        context = super(OwnBookingListView, self).get_context_data(**kwargs)
        permissions_list = []
        user = self.request.user

        for o in context['object_list']:
            # Заказ ждет выполнения
            if o.status == Booking.PENDING:
                if not user.has_perm("booking.add_booking"):
                    # Тип пользователя - исполнитель.
                    if o.customer.profile.has_enough_cash_for_booking(o.price):
                        # Такие пользователи могут брать заказы на выполнение,
                        # если у заказчика достаточно средств
                        permissions_list.append(self.CAN_TAKE)
                    else:
                        # Иначе - кнопка взятия заказа неактивна
                        permissions_list.append(self.NOT_ACTIVE)
                else:
                    if o.customer.profile.has_enough_cash_for_booking(o.price):
                        # Остальные могут просматривать
                        permissions_list.append(self.CAN_VIEW)
                    else:
                        # Иначе - кнопка взятия заказа неактивна
                        permissions_list.append(self.NOT_ACTIVE)
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
                    else:
                        if o.status == Booking.WAITING_FOR_APPROVAL:
                            # Заказ ждет подтверждения заказчиком после попытки
                            # исполнителя его взять
                            if not user.has_perm("booking.add_booking"):
                                # Для исполнителя кнопка заказа неактивна
                                permissions_list.append(self.NOT_ACTIVE)
                            else:
                                # Заказчик может подтрверждать/отклонять,
                                # если создавал этот заказ
                                if o.customer == user:
                                    permissions_list.append(self.CAN_APPROVE)
                                else:
                                    permissions_list.append(self.CAN_VIEW)


        context['bookings'] = zip(context['object_list'], permissions_list)
        context['page_type'] = "own_bookings"
        return context


class DeleteBookingView(LoginRequiredMixin, DeleteView):
    """
    Удаление заказа.
    Необходимо сделать удаление комментариев заказа.
    """

    model = Booking

    def get_success_url(self):
        """
        Редирект на страницу всех заказов или на страницу заказов пользователя
        """
        page = self.request.GET.get("page", None)
        if page == "own_bookings":
            return reverse_lazy('own-booking-list')
        else:
            if page == "all_bookings":
                return reverse_lazy('booking-list')
        return reverse_lazy('booking-list')

    def get_object(self, queryset=None):
        """ Заказ создавался request.user. """
        booking = super(DeleteBookingView, self).get_object()
        if booking.customer != self.request.user:
            raise Http404
        # Если заказ выполняется, удалять его нельзя
        status = booking.get_status()
        if status == Booking.RUNNING or status == Booking.WAITING_FOR_APPROVAL:
            raise Http404

        return booking

    def delete(self, request, *args, **kwargs):
        Comment.objects.filter(booking=self.get_object()).delete()
        return super(DeleteBookingView, self).delete(request, *args, **kwargs)


class UpdateBookingView(UpdateView):
    """
    Обновление заказа
    """

    model = Booking
    fields = ['title', 'text']
    success_url = reverse_lazy('booking-list')
    template_name_suffix = '_update_form'

    @method_decorator(login_required)
    @method_decorator(permission_required('booking.add_booking',
        raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(UpdateBookingView, self).dispatch(*args, **kwargs)

    def get_object(self, queryset=None):
        """ Заказ создавался текущим пользователем """
        booking = super(UpdateBookingView, self).get_object()
        if booking.customer != self.request.user:
            raise Http404
        return booking


class BookingDetailView(LoginRequiredMixin, DetailView):
    """
    Детализированный вид заказа.
    Сюда же включен список комментариев к нему.
    """
    model = Booking

    def get_context_data(self, **kwargs):
        context = super(BookingDetailView, self).get_context_data(**kwargs)
        context['comments'] = reversed(self.object.booking_comments.all())
        return context

    def get_object(self, queryset=None):
        """ Текущий пользователь - создатель или исполнитель заказа """
        booking = super(BookingDetailView, self).get_object()
        if booking.customer != self.request.user and\
           booking.performer != self.request.user:
            raise Http404
        return booking


class CreateCommentView(LoginRequiredMixin, CreateView):
    """
    Создание заказа
    """

    model = Comment
    fields = ['text']
    form_class = CommentForm

    def get_success_url(self):
        """
        Редирект на страницу всех заказов или на страницу заказов пользователя
        """
        booking_id = self.request.POST.get('booking')
        if booking_id == "":
            raise Http404

        return reverse('booking-detail', kwargs={"pk": booking_id})

    def form_valid(self, form):
        comment = form.save(commit=False)
        booking_id = self.request.POST.get('booking')
        if booking_id == "":
            raise Http404

        booking = Booking.objects.get(id=booking_id)

        # Пользователь должен быть либо исполнителем заказа,
        # либо создателем, но, если он исполнитель и его заявка пока что не
        # подтверждена, он не может комментировать
        if booking.customer != self.request.user and\
           booking.performer != self.request.user or\
           (booking.performer == self.request.user and\
            booking.status == Booking.WAITING_FOR_APPROVAL):
            raise Http404
        comment.booking = booking
        comment.creator = self.request.user
        comment.save()
        return HttpResponseRedirect(self.get_success_url())
