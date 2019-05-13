import datetime

import dateutil.parser
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Button
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import UpdateView, CreateView, DeleteView
from django.views.generic.detail import SingleObjectMixin
from rest_framework import generics

from reservation.models import Car, Reservation, ChargingReservation
from reservation.serializers import ReservationSerializer, ChargingReservationSerializer


def index(request):
    if request.user.is_authenticated:
        return redirect('reservation:calendar')
    else:
        return redirect('login')


@login_required
def calendar(request):
    default_car = Car.objects.filter(users__in=[request.user]).first()
    return redirect('reservation:calendar_car', car_id=default_car.id)


# class CalendarCar(LoginRequiredMixin, UserPassesTestMixin, DetailView):
#     model = Car
#     template_name = 'reservation/calendar.html'
#
#     def test_func(self):
#         return self.request.user.car_set.filter(pk=self.kwargs['pk']).exists()
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         print(context)
#         context['cars'] = self.request.user.car_set.all()


@login_required
def calendar_car(request, car_id):
    car = get_object_or_404(Car, pk=car_id)
    if not request.user.car_set.filter(pk=car_id).exists():
        raise Http404()

    context = {
        'current_car': car,
        'cars': request.user.car_set.all()
    }

    return render(request, 'reservation/calendar.html', context)


class CarConfig(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = 'reservation/car_config.html'
    model = Car
    fields = ('name', 'summer_driving_range', 'winter_driving_range', 'charging_time')

    def get_success_url(self):
        return reverse('reservation:calendar_car', kwargs={'car_id': self.kwargs['pk']})

    def test_func(self):
        return self.request.user.car_set.filter(pk=self.kwargs['pk']).exists()


class ReservationDetail(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = 'reservation/reservation_detail.html'
    model = Reservation
    fields = ('description', 'distance', 'location', 'start_time', 'end_time', 'should_be_charged_fully', 'priority')

    def test_func(self):
        car_id = self.get_object().car.id
        return self.request.user.car_set.filter(pk=car_id).exists()

    def get_success_url(self):
        return reverse('reservation:calendar_car', kwargs={'car_id': self.get_object().car.id})

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()
        form.helper.add_input(Submit('submit', 'Update'))
        form.helper.add_input(Button('delete', 'Delete', onclick="deleteReservation()",
                                     css_class='btn-danger'))
        return form


class ReservationDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Reservation

    def test_func(self):
        car_id = self.get_object().car.id
        return self.request.user.car_set.filter(pk=car_id).exists()

    def get_success_url(self):
        return reverse('reservation:calendar_car', kwargs={'car_id': self.get_object().car.id})


class ReservationAdd(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    template_name = 'reservation/reservation_detail.html'
    model = Reservation
    fields = ('description', 'distance', 'location', 'start_time', 'end_time', 'should_be_charged_fully', 'priority')

    def test_func(self):
        car_id = self.kwargs['car_id']
        return self.request.user.car_set.filter(pk=car_id).exists()

    def get_initial(self):
        initial = super().get_initial()
        start_time = datetime.datetime.fromtimestamp(int(self.request.GET['time']))
        end_time = start_time + datetime.timedelta(hours=1)
        initial['start_time'] = start_time
        initial['end_time'] = end_time
        return initial

    def get_success_url(self):
        return reverse('reservation:calendar_car', kwargs={'car_id': self.kwargs['car_id']})

    def form_valid(self, form):
        form.instance.car = Car.objects.get(pk=self.kwargs['car_id'])
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()
        form.helper.add_input(Submit('submit', 'Create'))
        return form


class APIReservationsList(LoginRequiredMixin, UserPassesTestMixin, generics.ListAPIView):
    serializer_class = ReservationSerializer

    def test_func(self):
        return self.request.user in Car.objects.get(pk=self.kwargs['pk']).users.all()

    def get_queryset(self):
        start_time = dateutil.parser.parse(self.request.GET['start'])
        end_time = dateutil.parser.parse(self.request.GET['end'])
        return Reservation.objects.filter(car__id=self.kwargs['pk'], start_time__range=(start_time, end_time))


class APIChargingReservationsList(LoginRequiredMixin, UserPassesTestMixin, generics.ListAPIView):
    serializer_class = ChargingReservationSerializer

    def test_func(self):
        return self.request.user in Car.objects.get(pk=self.kwargs['pk']).users.all()

    def get_queryset(self):
        start_time = dateutil.parser.parse(self.request.GET['start'])
        end_time = dateutil.parser.parse(self.request.GET['end'])
        return ChargingReservation.objects.filter(car__id=self.kwargs['pk'], start_time__range=(start_time, end_time))
