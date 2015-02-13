from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import permission_required

from .models import Booking
from .forms import BookingForm
from Booking.views import LoginRequiredMixin


class BookingCreate(LoginRequiredMixin, CreateView):
    model = Booking
    fields = ['title', 'text', 'price']
    form_class = BookingForm
    success_url = '/home/'

    @method_decorator(login_required)
    @method_decorator(permission_required('booking.add_booking', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(BookingCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.customer = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())
