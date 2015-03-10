# -*- coding: utf-8 -*-

"""
Views, общие для проекта.
"""

from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.contrib.auth import authenticate
from django.contrib.auth.views import login
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.core.urlresolvers import reverse
from registration.backends.simple.views import RegistrationView
from registration.signals import user_registered
from django.contrib.auth.models import Group
from booking.models import UserProfile


class HomepageView(TemplateView):
    """
    Сюда попадает пользователь после входа.
    """
    template_name = "homepage.html"


class LoginRequiredMixin(object):

    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


def user_login(request):
    """
    Имплементация формы авторизации
    """
    # Like before, obtain the context for the user's request.
    context = RequestContext(request)

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect('/booking/booking_list/')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse(u"Ваш аккаунт неактивен.")
        else:
            # Bad login details were provided. So we can't log the user in.
            messages.error(request, u'Неверные параметры входа')
            return render_to_response('registration/login.html', {}, context)

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render_to_response('registration/login.html', {}, context)


# Create a new class that redirects the user to the index page, if successful at logging
class BookingRegistrationView(RegistrationView):

    def get_success_url(self, request, user):
        return reverse('booking-list')


def user_registered_callback(sender, user, request, **kwargs):
    """
    Сразу после регистрации пользователя по этому сигналу ему назначается группа
    (customers/performers), для него создается профиль.
    Сохраняется.
    """
    user_type = request.POST["user_type"]

    if user_type == "customer":
        customers = Group.objects.get(name="customers")
        # Назначение пользователю группы
        user.groups.add(customers)
        user.save()
        UserProfile.objects.create(user=user, cash=1000.00)
    else:
        performers = Group.objects.get(name="performers")
        user.groups.add(performers)
        user.save()
        UserProfile.objects.create(user=user, cash=1000.00)

user_registered.connect(user_registered_callback)
