from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.http import HttpResponseRedirect

from .models import Booking
from .forms import BookingForm


class BookingCreate(CreateView):
    model = Booking
    fields = ['title', 'text', 'price']
    form_class = BookingForm
    success_url = '/'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.customer = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())
