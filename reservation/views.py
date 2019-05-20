import datetime

import dateutil.parser
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import UpdateView, CreateView, DeleteView
from django.views.generic.detail import SingleObjectMixin, DetailView
from rest_framework import generics

from reservation.forms import ReservationDetailForm, ReservationAddForm, ChargingReservationAddForm, \
    ChargingReservationDetailForm
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
    return redirect('reservation:calendar_car', pk=default_car.id)


class CalendarCar(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Car
    template_name = 'reservation/calendar.html'

    def test_func(self):
        return self.get_object() in self.request.user.car_set.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_cars'] = self.request.user.car_set.all()
        return context


class CarConfig(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = 'reservation/car_config.html'
    model = Car
    fields = ('name', 'summer_driving_range', 'winter_driving_range', 'charging_time')

    def get_success_url(self):
        return reverse('reservation:calendar_car', kwargs={'pk': self.kwargs['pk']})

    def test_func(self):
        return self.request.user.car_set.filter(pk=self.kwargs['pk']).exists()


class ReservationDetail(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = 'reservation/reservation_detail.html'
    model = Reservation
    form_class = ReservationDetailForm

    def test_func(self):
        car_id = self.get_object().car.id
        return self.request.user.car_set.filter(pk=car_id).exists()

    def get_success_url(self):
        return reverse('reservation:calendar_car', kwargs={'pk': self.get_object().car.id})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['car'] = self.get_object().car
        kwargs['owner'] = self.get_object().owner
        kwargs['id'] = self.get_object().id
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['car'] = self.get_object().car
        context['reservation_type'] = 'reservation'
        return context


class ReservationDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Reservation

    def test_func(self):
        car_id = self.get_object().car.id
        return self.request.user.car_set.filter(pk=car_id).exists()

    def get_success_url(self):
        return reverse('reservation:calendar_car', kwargs={'pk': self.get_object().car.id})


class ReservationAdd(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    template_name = 'reservation/reservation_detail.html'
    model = Reservation
    form_class = ReservationAddForm

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.car = Car.objects.get(pk=self.kwargs['car_id'])

    def test_func(self):
        return self.request.user.car_set.filter(pk=self.car.id).exists()

    def get_initial(self):
        initial = super().get_initial()

        if 'time' in self.request.GET:
            start_time = datetime.datetime.fromtimestamp(int(self.request.GET['time']))
        else:
            start_time = datetime.datetime.now().replace(microsecond=0, second=0, minute=0)

        end_time = start_time + datetime.timedelta(hours=1)
        initial['start_time'] = start_time
        initial['end_time'] = end_time
        return initial

    def get_success_url(self):
        return reverse('reservation:calendar_car', kwargs={'pk': self.car.id})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['car'] = self.car
        kwargs['owner'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['car'] = Car.objects.get(pk=self.kwargs['car_id'])
        context['reservation_type'] = 'reservation'
        return context


class ChargingReservationDetail(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = 'reservation/reservation_detail.html'
    model = ChargingReservation
    form_class = ChargingReservationDetailForm

    def test_func(self):
        car_id = self.get_object().car.id
        return self.request.user.car_set.filter(pk=car_id).exists()

    def get_success_url(self):
        return reverse('reservation:calendar_car', kwargs={'pk': self.get_object().car.id})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['car'] = self.get_object().car
        kwargs['id'] = self.get_object().id
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reservation_type'] = 'charging_reservation'
        context['car'] = self.get_object().car
        return context


class ChargingReservationDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = ChargingReservation

    def test_func(self):
        car_id = self.get_object().car.id
        return self.request.user.car_set.filter(pk=car_id).exists()

    def get_success_url(self):
        return reverse('reservation:calendar_car', kwargs={'pk': self.get_object().car.id})


class ChargingReservationAdd(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    template_name = 'reservation/reservation_detail.html'
    model = ChargingReservation
    form_class = ChargingReservationAddForm

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.car = Car.objects.get(pk=self.kwargs['car_id'])

    def test_func(self):
        return self.request.user.car_set.filter(pk=self.car.id).exists()

    def get_initial(self):
        initial = super().get_initial()

        if 'time' in self.request.GET:
            start_time = datetime.datetime.fromtimestamp(int(self.request.GET['time']))
        else:
            start_time = datetime.datetime.now().replace(microsecond=0, second=0, minute=0)

        end_time = start_time + datetime.timedelta(hours=self.car.charging_time)
        initial['start_time'] = start_time
        initial['end_time'] = end_time
        return initial

    def get_success_url(self):
        return reverse('reservation:calendar_car', kwargs={'pk': self.car.id})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['car'] = self.car
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['car'] = self.car
        context['reservation_type'] = 'charging_reservation'
        return context


class DistanceLeft(LoginRequiredMixin, UserPassesTestMixin, SingleObjectMixin, View):
    model = Car

    def test_func(self):
        car_id = self.get_object().id
        return self.request.user.car_set.filter(pk=car_id).exists()

    def get(self, request, *args, **kwargs):
        if 'time' in request.GET:
            time = datetime.datetime.fromtimestamp(int(request.GET['time']))
        else:
            time = datetime.datetime.now().replace(microsecond=0, second=0, minute=0)
        return JsonResponse({
            'distance_left': self.get_object().get_distance_left(time),
            'driving_range': self.get_object().get_driving_range(time)
        })


class APIReservationsList(LoginRequiredMixin, UserPassesTestMixin, generics.ListAPIView):
    serializer_class = ReservationSerializer

    def test_func(self):
        return self.request.user in Car.objects.get(pk=self.kwargs['pk']).users.all()

    def get_queryset(self):
        start_time = dateutil.parser.parse(self.request.GET['start'])
        end_time = dateutil.parser.parse(self.request.GET['end'])
        return Reservation.objects. \
            filter(Q(car__id=self.kwargs['pk']) &
                   (Q(start_time__range=(start_time, end_time)) | Q(end_time__range=(start_time, end_time))))


class APIChargingReservationsList(LoginRequiredMixin, UserPassesTestMixin, generics.ListAPIView):
    serializer_class = ChargingReservationSerializer

    def test_func(self):
        return self.request.user in Car.objects.get(pk=self.kwargs['pk']).users.all()

    def get_queryset(self):
        start_time = dateutil.parser.parse(self.request.GET['start'])
        end_time = dateutil.parser.parse(self.request.GET['end'])
        return ChargingReservation.objects. \
            filter(Q(car__id=self.kwargs['pk']) &
                   (Q(start_time__range=(start_time, end_time)) | Q(end_time__range=(start_time, end_time))))
